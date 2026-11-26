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

The output directory receives `OrangeFox-R12.0-Unofficial-p3s-Test6.tar`, the corresponding raw recovery image, their SHA-256 checksums, and a record of the source revisions and patches used for the build. The device changes and Android platform revisions are in [`patches/`](patches/).

The published recipe was checked against the tested checkout and image. A clean build using the published recipe is still pending verification.

## Test 2 device results

Test 2 booted into OrangeFox and USB ADB worked. Samsung Keymaster 4.0 registered about 13 seconds after launch, following a wait for StrongBox. Recovery's five-second timeout stopped the attempt before it mounted `/data`. The previous TWRP was restored, and encrypted storage was accessible after booting Android 17 again.

## Test 3 device results

Test 3 booted, USB ADB worked, and Samsung Keymaster 4.0 registered within the new 25-second timeout. Keystore2 could not read its ODM VINTF manifest path because the mounted vendor's `/vendor/odm` link returned to `/odm`, while recovery's fallback `/odm/etc` link pointed into `/vendor/odm/etc`. Encrypted `/data` remained unmounted. TWRP was restored and encrypted storage was accessible again in Android 17.

## Test 4 device results

Test 4 booted and USB ADB worked. Recovery mounted the real `/odm` partition read-only, both Keymaster and Keystore2 registered, and the metadata-encrypted F2FS `/data` volume mounted through a device mapper. Device-encrypted key setup then failed because recovery's session lacked the `fscrypt` keyring. TWRP was restored and encrypted storage was accessible again in Android 17.

## Test 5 device results

Test 5 booted, USB ADB worked, and recovery mounted `/data` and loaded the device-encrypted key. Credential-encrypted access stopped because recovery could not find the Samsung Weaver service. TWRP was restored and encrypted storage remained accessible in Android 17.

## Test 6

Test 6 declares Weaver 1.0 and starts the installed Samsung `hermesd` on demand when the existing enrollment requires Weaver. It gives Hermes a temporary RAM overlay for its existing state directory and masks the vendor's secure-element firmware files during recovery. Recovery stops the attempt if those protections cannot be set up or the service does not register. Test 6 retains the working kernel, modules, USB configuration, recovery fstab, and existing-key safeguards.

On-device acceptance requires recovery boot, USB ADB, mapped F2FS `/data`, device-encrypted key setup, Weaver registration, and read access to existing credential-encrypted storage after the owner enters their usual PIN. Keep the original recovery available for rollback. Test 6 decryption on the Android 17 ROM is pending device verification.

See [NOTICE.md](NOTICE.md) for attribution and upstream licensing information.
