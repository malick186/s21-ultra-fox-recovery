# S21 Ultra Fox Recovery

Unofficial OrangeFox R12.0 for the Samsung Galaxy S21 Ultra 5G Exynos (`SM-G998B`, `p3s`). Source revisions are recorded in [`sources.env`](sources.env).

**Test 11 is the first build in this series to pass recovery boot, USB ADB, and PIN-based `/data` decryption.** This was verified on one SM-G998B running a custom Android 17 ROM. USB ADB connected after toggling MTP.

[Download Test 11](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test11) · [Changelog for Tests 1–11](CHANGELOG.md) · [All releases](https://github.com/malick186/s21-ultra-fox-recovery/releases)

Each prerelease includes a recovery-only Odin TAR, the matching raw recovery image, SHA-256 checksums, and a record of the build inputs.

This branch contains the Test 11 build recipe and the source history for the storage decryption tests.

## Build

Use a non-root account on 64-bit Linux. Keep both build and output directories on a Linux filesystem and use paths without spaces. The OrangeFox build guide specifies at least 45 GB of storage for this build environment. [OrangeFox build guide](https://wiki.orangefox.tech/dev/building)

With Ubuntu, install the host dependencies using `bash scripts/install-deps-ubuntu.sh`. Make the Android Repo launcher available on `PATH`. [Android Repo setup](https://source.android.com/docs/setup/start/requirements#install-repo)

Run the following from the repository root.

```bash
bash scripts/build.sh "$HOME/orangefox-p3s-build" "$HOME/orangefox-p3s-artifacts"
```

The output directory receives `OrangeFox-R12.0-Unofficial-p3s-Test11.tar`, the corresponding raw recovery image, their SHA-256 checksums, and a record of the source revisions and patches used for the build. The device changes and Android platform revisions are in [`patches/`](patches/).

The published recipe was checked against the tested checkout and image. A clean build using the published recipe is still pending verification.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
