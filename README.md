# S21 Ultra Fox Recovery

**R13 Stable** is the S21 Ultra Fox Recovery community release for the Samsung Galaxy S21 Ultra 5G Exynos (`SM-G998B`, `p3s`). The recovery is based on OrangeFox R12.0, which is the version shown on the device.

The release uses Test 11's recovery code, kernel, and USB setup. Test 11 passed recovery boot, USB ADB, and PIN-based access to credential-encrypted `/data` on one SM-G998B running a custom Android 17 ROM with bootloader `G998BXXSJHZC2`. USB ADB connected after toggling MTP. R13 replaces the workstation build hostname with a generic value and updates the image checksums.

[Download R13 Stable](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r13.0-p3s-stable) · [Install and roll back](INSTALL.md) · [Full changelog](CHANGELOG.md) · [XDA post draft](docs/XDA.md)

The release includes a recovery-only Odin TAR, the matching raw recovery image, SHA-256 checksums, and a record of the build inputs. The install guide covers upgrading an existing custom recovery on an unlocked SM-G998B.

## Build

Use a non-root account on 64-bit Linux. Keep both build and output directories on a Linux filesystem and use paths without spaces. The OrangeFox build guide specifies at least 45 GB of storage for this build environment. [OrangeFox build guide](https://wiki.orangefox.tech/dev/building)

With Ubuntu, install the host dependencies using `bash scripts/install-deps-ubuntu.sh`. Make the Android Repo launcher available on `PATH`. [Android Repo setup](https://source.android.com/docs/setup/start/requirements#install-repo)

Run the following from the repository root.

```bash
bash scripts/build.sh "$HOME/orangefox-p3s-build" "$HOME/orangefox-p3s-artifacts"
```

The build produces an R13 Odin TAR, raw recovery image, SHA-256 checksums, and a build-input record. [`sources.env`](sources.env) and [`patches/`](patches/) specify the source inputs. The public downloads come from repackaging the Test 11 image with generic build-host metadata using [`scripts/sanitize-release.py`](scripts/sanitize-release.py).

The Test 11 recipe was verified with the pinned build cache. A fresh build may have different image hashes because Android embeds build metadata.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
