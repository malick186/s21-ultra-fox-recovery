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

The output directory receives `OrangeFox-R12.0-Unofficial-p3s-May-kernel.tar`, its SHA-256 checksum, and a record of the source revisions used for that build. The device changes and the exact Android platform revisions are in [`patches/`](patches/).

The published recipe was checked against the tested checkout and image. A clean build using the published recipe is still pending verification.

## Next version

The next milestone is encrypted storage access on the tested Android 17 ROM. A device test should validate the `/data` mount and credential-encrypted storage access alongside recovery boot and USB ADB.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
