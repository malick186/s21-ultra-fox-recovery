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

The output directory receives `OrangeFox-R12.0-Unofficial-p3s-Test2.tar`, the corresponding raw recovery image, their SHA-256 checksums, and a record of the source revisions and patches used for the build. The device changes and Android platform revisions are in [`patches/`](patches/).

The published recipe was checked against the tested checkout and image. A clean build using the published recipe is still pending verification.

## Test 2

Test 2 enables file-based and metadata encryption support with Samsung's TEEGRIS and HIDL Keymaster 4.0 from the mounted vendor partition. Recovery opens the existing metadata key directory on a read-only mount and begins the key operation after Keymaster and Keystore2 register. If the keys are unavailable or a storage key blob requires upgrading, the attempt stops. Recovery reads the existing device and user keys without generating replacement keys or cleaning up old credential keys. Test 2 retains the Test 1 kernel, modules, USB configuration, and filesystem definitions. The recovery ramdisk uses maximum gzip compression to stay within the 64 MiB partition.

On-device acceptance requires recovery boot, USB ADB, a working F2FS `/data` mount through the mapped volume, and access to an existing test file after the owner unlocks credential-encrypted storage. Test against the existing encrypted storage and retain the original recovery for rollback. Decryption on the tested Android 17 ROM is pending device verification.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
