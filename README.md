# S21 Ultra Fox Recovery

Unofficial OrangeFox R12.0 build sources for the Samsung Galaxy S21 Ultra 5G Exynos (`SM-G998B`, `p3s`). The baseline pairs the May kernel with its matching modules and records the source revisions in [`sources.env`](sources.env).

## Tested baseline

| Check | Result on `SM-G998B` |
| --- | --- |
| Recovery boot | OrangeFox reached the recovery interface. |
| USB ADB | Connected successfully in recovery. |
| Recovery image size | 63,549,456 bytes, within the 64 MiB partition. |
| Encrypted internal storage | Recovery failed to mount `/data`. Android 17 mounted the same encrypted F2FS storage normally. |

The device was returned to TWRP and Android boot was verified after the tests. The test results apply to the listed model and the ROM used for testing.

## Build

Use a non-root account on 64-bit Linux. Keep both build and output directories on a Linux filesystem and use paths without spaces. The OrangeFox build guide specifies at least 45 GB of storage for this build environment. [OrangeFox build guide](https://wiki.orangefox.tech/dev/building)

With Ubuntu, install the host dependencies using `bash scripts/install-deps-ubuntu.sh`. Make the Android Repo launcher available on `PATH`. [Android Repo setup](https://source.android.com/docs/setup/start/requirements#install-repo)

Run the following from the repository root.

```bash
bash scripts/build.sh "$HOME/orangefox-p3s-build" "$HOME/orangefox-p3s-artifacts"
```

The output directory receives `OrangeFox-R12.0-Unofficial-p3s-Test3.tar`, the corresponding raw recovery image, their SHA-256 checksums, and a record of the source revisions and patches used for the build. The device changes and Android platform revisions are in [`patches/`](patches/).

The published recipe was checked against the tested checkout and image. A clean build using the published recipe is still pending verification.

## Test 2 device results

Test 2 booted into OrangeFox and USB ADB worked. Samsung Keymaster 4.0 registered about 13 seconds after launch, following a wait for StrongBox. Recovery's five-second timeout stopped the attempt before it mounted `/data`. The previous TWRP was restored, and encrypted storage was accessible after booting Android 17 again.

## Test 3

Test 3 allows 25 seconds for Samsung Keymaster 4.0 registration and logs when Keymaster and Keystore2 register. It retains the Test 2 kernel, modules, USB configuration, and filesystem definitions. It mounts `/metadata` read-only, uses the existing encryption keys, and stops if those keys are unavailable or require an upgrade. The recovery ramdisk uses maximum gzip compression to stay within the 64 MiB partition.

On-device acceptance requires recovery boot, USB ADB, a working F2FS `/data` mount through the mapped volume, and read access to existing credential-encrypted storage after the owner enters their usual PIN. Keep the original recovery available for rollback. Test 3 decryption on the Android 17 ROM is pending device verification.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
