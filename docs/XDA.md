# [RECOVERY] S21 Ultra Fox Recovery R13 Stable for SM-G998B (Exynos)

R13 Stable is an unofficial community release for the Galaxy S21 Ultra 5G Exynos **SM-G998B (`p3s`)**. It uses OrangeFox R12.0 as its recovery base.

## What passed

- Recovery boot and USB ADB on one SM-G998B with bootloader `G998BXXSJHZC2` and a custom Android 17 ROM. USB ADB connected after toggling MTP.
- The existing Android PIN unlocked `/data`. ADB confirmed access to credential-encrypted storage.
- Samsung Weaver started for verification and stopped afterward.

R13 packages the tested Test 11 recovery code and kernel with generic build-host metadata. The on-device check covered boot, USB, and PIN decryption on that setup. Backup and restore, stock ROMs, and other firmware combinations are outside that hardware test.

[Download the recovery-only Odin TAR, raw image and SHA-256 file](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r13.0-p3s-stable)

## Flash and roll back

Use on an unlocked SM-G998B with an existing compatible custom-recovery setup. Confirm the model in Download Mode and keep a known-working recovery package and a separate copy of your files. Flash the Odin TAR in AP, or flash the raw image to Recovery from compatible TWRP. [Full installation and rollback guide](https://github.com/malick186/s21-ultra-fox-recovery/blob/r13.0-p3s-stable/INSTALL.md)

For reports, include the model, bootloader version, ROM, and which of boot, USB, or storage failed. Share only relevant, redacted log lines. Keep device identifiers, account details, PINs, and backups private. [Report an issue](https://github.com/malick186/s21-ultra-fox-recovery/issues)

[Release source and patches](https://github.com/malick186/s21-ultra-fox-recovery/tree/r13.0-p3s-stable) · [Device tree and kernel attribution](https://github.com/malick186/s21-ultra-fox-recovery/blob/r13.0-p3s-stable/NOTICE.md) · [Changelog](https://github.com/malick186/s21-ultra-fox-recovery/blob/r13.0-p3s-stable/CHANGELOG.md)
