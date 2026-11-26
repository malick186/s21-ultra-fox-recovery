#!/usr/bin/env bash
set -Eeo pipefail

if [[ $# -ne 2 || $(id -u) -eq 0 ]]; then
    printf 'Usage as a regular user: bash %s BUILD_ROOT OUTPUT_DIR\n' "$0" >&2
    exit 2
fi

project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
source "$project_root/sources.env"
build_jobs=${BUILD_JOBS:-4}
sync_jobs=${SYNC_JOBS:-2}
if [[ ! $build_jobs =~ ^[1-9][0-9]*$ || ! $sync_jobs =~ ^[1-9][0-9]*$ ]]; then
    printf 'BUILD_JOBS and SYNC_JOBS must be positive integers.\n' >&2
    exit 2
fi
for tool in git repo python3 tar sha256sum; do
    command -v "$tool" >/dev/null || { printf 'Missing tool: %s\n' "$tool" >&2; exit 2; }
done

mkdir -p -- "$1" "$2"
build_root=$(cd -- "$1" && pwd -P)
output_dir=$(cd -- "$2" && pwd -P)
if [[ $build_root =~ [[:space:]] ]]; then
    printf 'Choose a build root without whitespace for the upstream sync script.\n' >&2
    exit 2
fi
sync_dir="$build_root/sync"
source_dir="$build_root/fox_12.1"
device_dir="$source_dir/device/samsung/exynos2100"
platform_lock="$project_root/patches/platform-revisions.xml"
sync_stamp="$build_root/.p3s-source-sync-complete"
trap 'code=$?; printf "Build stopped at line %s (exit %s).\n" "$LINENO" "$code" >&2' ERR

export LC_ALL=C GIT_TERMINAL_PROMPT=0
export FOX_BUILD_DEVICE=p3s
export ALLOW_MISSING_DEPENDENCIES=true
export OF_DISABLE_MIUI_SPECIFIC_FEATURES=1
export OF_FORCE_PREBUILT_KERNEL=1
export OUT_DIR="$source_dir/out"

checkout() {
    local url=$1 revision=$2 directory=$3
    if [[ ! -d $directory/.git ]]; then
        git init "$directory"
        git -C "$directory" remote add origin "$url"
    fi
    if ! git -C "$directory" cat-file -e "$revision^{commit}" 2>/dev/null; then
        git -C "$directory" fetch --depth=1 origin "$revision"
    fi
    git -C "$directory" checkout --detach "$revision"
}

assert_revision() {
    local directory=$1 expected=$2 actual
    actual=$(git -C "$directory" rev-parse HEAD)
    if [[ $actual != "$expected" ]]; then
        printf 'Source revision drift in %s: got %s, expected %s.\n' "$directory" "$actual" "$expected" >&2
        exit 1
    fi
}

checkout "$SYNC_URL" "$SYNC_REV" "$sync_dir"

if [[ ! -f $sync_stamp ]]; then
    if [[ -e $source_dir && ! -f $build_root/.p3s-source-sync-started ]]; then
        printf 'The build root already contains an unmanaged fox_12.1 directory.\n' >&2
        exit 2
    fi
    if [[ -e $sync_dir/fox_12.1_manifest.sav ]]; then
        printf 'The previous sync stopped after applying upstream patches. Use a fresh build root.\n' >&2
        exit 2
    fi
    touch "$build_root/.p3s-source-sync-started"
    (
        cd -- "$sync_dir"
        sync_scratch=$(mktemp -d "$build_root/.sync.XXXXXXXX")
        trap 'rm -rf -- "$sync_scratch"' EXIT
        export ORANGEFOX_SYNC_SCRATCH="$sync_scratch"
        # Isolate the upstream script's temporary recovery checkout from other builds.
        sed -e 's@rm -rf /tmp/recovery@rm -rf "$ORANGEFOX_SYNC_SCRATCH/recovery"@g' \
            -e 's@mv recovery /tmp;@mv recovery "$ORANGEFOX_SYNC_SCRATCH";@' \
            orangefox_sync.sh > "$sync_scratch/orangefox_sync.sh"
        if grep -Eq 'rm -rf /tmp/recovery|mv recovery /tmp;' "$sync_scratch/orangefox_sync.sh"; then
            printf 'The upstream sync still uses a shared temporary checkout.\n' >&2
            exit 1
        fi
        export MANIFEST_REV MANIFEST_BRANCH REPO_REV platform_lock sync_jobs
        repo() {
            case "$1" in
                init)
                    command repo "$@" --manifest-branch="$MANIFEST_REV" \
                        --manifest-upstream-branch="$MANIFEST_BRANCH" --repo-rev="$REPO_REV" || return
                    install -D -m 644 "$platform_lock" .repo/local_manifests/p3s-platform-revisions.xml
                    ;;
                sync)
                    command repo "$@" --jobs="$sync_jobs" --retry-fetches=2 --no-manifest-update
                    ;;
                *) command repo "$@" ;;
            esac
        }
        export -f repo
        bash "$sync_scratch/orangefox_sync.sh" --branch 12.1 --path "$source_dir"
    )
    # OrangeFox sync substitutes these two Git checkouts after the Android platform sync.
    checkout "$RECOVERY_URL" "$RECOVERY_REV" "$source_dir/bootable/recovery"
    checkout "$VENDOR_URL" "$VENDOR_REV" "$source_dir/vendor/recovery"
    touch "$sync_stamp"
fi
assert_revision "$source_dir/.repo/manifests" "$MANIFEST_REV"
assert_revision "$source_dir/.repo/repo" "$REPO_REV"
assert_revision "$source_dir/bootable/recovery" "$RECOVERY_REV"
assert_revision "$source_dir/vendor/recovery" "$VENDOR_REV"

if [[ -d $device_dir/.git && $(git -C "$device_dir" rev-parse HEAD) == "$DEVICE_REV" ]]; then
    printf 'Using the existing pinned p3s device checkout.\n'
else
    mkdir -p -- "$(dirname -- "$device_dir")"
    checkout "$DEVICE_URL" "$DEVICE_REV" "$device_dir"
fi
assert_revision "$device_dir" "$DEVICE_REV"
if ! git -C "$device_dir" cat-file -e "$PREBUILT_REV^{commit}" 2>/dev/null; then
    git -C "$device_dir" fetch --depth=1 origin "$PREBUILT_REV"
fi
git -C "$device_dir" restore --source="$PREBUILT_REV" --staged --worktree -- \
    p3s/prebuilt p3s/recovery/root/lib/modules
printf '%s  %s\n' "$KERNEL_SHA256" "$device_dir/p3s/prebuilt/Image" | sha256sum -c -

device_patch="$project_root/patches/disable-extra-languages.patch"
if git -C "$device_dir" apply --unidiff-zero --check "$device_patch" 2>/dev/null; then
    git -C "$device_dir" apply --unidiff-zero "$device_patch"
elif ! git -C "$device_dir" apply --unidiff-zero --reverse --check "$device_patch"; then
    printf 'The device tree does not match the optional-language patch.\n' >&2
    exit 1
fi
grep -Fxq 'TW_EXTRA_LANGUAGES :=' "$device_dir/BoardConfig.mk"

apply_patch() {
    local directory=$1 patch="$project_root/patches/$2"
    if git -C "$directory" apply --check "$patch" 2>/dev/null; then
        git -C "$directory" apply "$patch"
    elif ! git -C "$directory" apply --reverse --check "$patch"; then
        printf 'Patch %s does not match %s.\n' "$patch" "$directory" >&2
        exit 1
    fi
}

apply_patch "$device_dir" enable-recovery-crypto.patch
apply_patch "$device_dir" p3s-legacy-vendor-crypto.patch
apply_patch "$source_dir/bootable/recovery" p3s-start-vendor-crypto.patch
apply_patch "$source_dir/system/vold" guard-recovery-key-upgrade.patch
apply_patch "$source_dir/system/vold" read-existing-storage-keys.patch
apply_patch "$source_dir/system/security" refuse-storage-key-upgrade.patch
apply_patch "$source_dir/build/make" compress-recovery-ramdisk.patch
apply_patch "$source_dir/build/make" stage-current-keystore2.patch
grep -Fxq 'TW_INCLUDE_CRYPTO := true' "$device_dir/BoardConfig.mk"

cd -- "$source_dir"
repo manifest -r -o "$build_root/checkout-revisions.xml"
python3 "$project_root/scripts/verify.py" platform "$platform_lock" "$build_root/checkout-revisions.xml"

source build/envsetup.sh || true
type lunch >/dev/null
type mka >/dev/null
lunch twrp_p3s-eng
mka "-j$build_jobs" recoveryimage

product_dir="$OUT_DIR/target/product/p3s"
python3 "$project_root/scripts/verify.py" image "$product_dir/recovery.img" "$KERNEL_SHA256"

name=OrangeFox-R12.0-Unofficial-p3s-Test3
tar --format=ustar -cf "$output_dir/$name.tar.partial" -C "$product_dir" recovery.img
[[ $(tar -tf "$output_dir/$name.tar.partial") == recovery.img ]]
{
    printf 'target=twrp_p3s-eng\nsync=%s\nrepo=%s\nmanifest=%s\n' "$SYNC_REV" "$REPO_REV" "$MANIFEST_REV"
    printf 'recovery=%s\nvendor=%s\ndevice=%s\np3s_kernel_and_modules=%s\n' \
        "$RECOVERY_REV" "$VENDOR_REV" "$DEVICE_REV" "$PREBUILT_REV"
    printf 'platform_revisions_sha256=%s\n' "$(sha256sum "$platform_lock" | cut -d ' ' -f1)"
    (cd -- "$project_root" && sha256sum patches/*.patch)
} > "$output_dir/$name-sources.txt"
cp -- "$product_dir/recovery.img" "$output_dir/$name-recovery.img.partial"
mv -- "$output_dir/$name-recovery.img.partial" "$output_dir/$name-recovery.img"
mv -- "$output_dir/$name.tar.partial" "$output_dir/$name.tar"
(cd -- "$output_dir" && sha256sum "$name.tar" "$name-recovery.img" > "$name.sha256")
printf 'Package: %s\n' "$output_dir/$name.tar"
