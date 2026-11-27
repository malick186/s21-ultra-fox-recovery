# S21 Ultra Fox Recovery

Unofficial OrangeFox R12.0 for the Samsung Galaxy S21 Ultra 5G Exynos (`SM-G998B`, `p3s`). Source revisions are recorded in [`sources.env`](sources.env).

This branch contains the Test 11 build recipe and the source history for the storage decryption tests.

## Test prereleases

Each release includes the recovery-only Odin TAR, the matching raw recovery image, SHA-256 checksums, and a build-input record. [All releases](https://github.com/malick186/s21-ultra-fox-recovery/releases)

Recovery boot and USB ADB worked in all seven tests on the same SM-G998B with a custom Android 17 ROM. PIN-based access to credential-encrypted storage remains unresolved. The phone was returned to TWRP and encrypted storage was accessible again in Android after the tests.

| Prerelease | Source used for the build | Device result |
| --- | --- | --- |
| [Test 1](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test1) | [`r12.0-p3s-test1`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test1) | Encrypted `/data` stayed unmounted. |
| [Test 2](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test2) | [`r12.0-p3s-test2`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test2) | Keymaster registered after the five-second deadline. `/data` stayed unmounted. |
| [Test 3](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test3) | [`r12.0-p3s-test3`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test3) | Keymaster registered. Keystore2 hit the ODM VINTF symlink loop before `/data` could mount. |
| [Test 4](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test4) | [`r12.0-p3s-test4`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test4) | The read-only ODM mount and Keystore2 worked. `/data` mounted, then device-encrypted key setup failed at the fscrypt session keyring. |
| [Test 5](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test5) | [`r12.0-p3s-test5`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test5) | `/data` mounted and the device-encrypted key loaded. Weaver was unavailable for credential unlock. |
| [Test 6](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test6) | [`r12.0-p3s-test6`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test6) | `/data` mounted. The kernel rejected the Weaver state overlay before Hermes could start. |
| [Test 7](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test7) | [`r12.0-p3s-test7`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test7) | `/data` mounted. The Weaver RAM copy stayed empty and Hermes never started. Credential-encrypted folders stayed locked. |

Test 8 booted and USB ADB connected. `/data` mounted, and recovery still reported the credential-encrypted storage as locked after PIN entry. The verified TWRP image was restored.

Test 9 booted, USB ADB connected, and the Weaver slot decoded successfully. Credential-encrypted storage stayed locked, and Hermes did not register. The verified TWRP image was restored.

Test 10 booted and connected over USB. The mount namespace, firmware directory, K250A node, and read-only Weaver directory checks passed up to `fdopendir`. Android's file-descriptor sanitizer then aborted recovery before Hermes started. The verified TWRP image was restored.

Test 11 uses Android's `Fdopendir` helper to transfer the directory descriptor from `unique_fd` before Bionic takes ownership. The pre-PIN diagnostics and protected Hermes startup remain in place. Device verification is pending.

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
