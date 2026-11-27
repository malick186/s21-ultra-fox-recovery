# OrangeFox R12.0 changelog

Unofficial builds for the Samsung Galaxy S21 Ultra 5G Exynos (`SM-G998B`, `p3s`). Device results are from one phone running a custom Android 17 ROM. Recovery boot and USB ADB worked in all eleven tests. Test 11 was the first to confirm PIN-based access to credential-encrypted `/data`. The original TWRP was restored after Tests 1–10.

## Test 11

Transferred the directory descriptor with the Android `Fdopendir` helper before Bionic took ownership. Kept the pre-PIN diagnostics, protected RAM copy, and read-only firmware mask.

Recovery booted and USB ADB connected after toggling MTP. The existing Android PIN unlocked `/data`, and ADB confirmed credential-encrypted storage was readable. Weaver registered and shut down after verification. Test 11 remained installed.

[Download Test 11](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test11) · [Source `r12.0-p3s-test11`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test11)

## Test 10

Added pre-PIN diagnostics for the mount namespace, firmware directory, K250A device, and existing Weaver state. Limited the wait for the diagnostic to one second.

The prerequisite checks passed through `fstat`. The Android file-descriptor sanitizer aborted recovery at `fdopendir` before Hermes could start. Credential-encrypted storage stayed locked.

[Download Test 10](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test10) · [Source `r12.0-p3s-test10`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test10)

## Test 9

Corrected Android Weaver slot decoding and validated the slot against the hardware range. Added a registration check without lazy startup and rejected unknown FBE users.

The slot decoded successfully and `/data` mounted. Hermes did not register, and credential-encrypted storage stayed locked.

[Download Test 9](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test9) · [Source `r12.0-p3s-test9`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test9)

## Test 8

Opened and pinned the existing Weaver state directory read-only before RAM setup, then rechecked its identity before the bind mount.

`/data` mounted. Recovery still reported user 0 as locked after PIN entry, and the encrypted-storage read check failed.

[Download Test 8](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test8) · [Source `r12.0-p3s-test8`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test8)

## Test 7

Replaced OverlayFS with a protected RAM snapshot for Weaver state and a read-only firmware mask.

`/data` mounted. The RAM snapshot stayed empty, Hermes did not start, and credential-encrypted storage stayed locked.

[Download Test 7](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test7) · [Source `r12.0-p3s-test7`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test7)

## Test 6

Added the Samsung Weaver provider and attempted to isolate its state writes with OverlayFS.

`/data` mounted. The kernel rejected the state overlay, Hermes did not start, and credential-encrypted storage stayed locked.

[Download Test 6](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test6) · [Source `r12.0-p3s-test6`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test6)

## Test 5

Initialized the fscrypt session keyring during recovery boot.

`/data` mounted and the device-encrypted key loaded. Weaver was unavailable, so credential-encrypted storage stayed locked.

[Download Test 5](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test5) · [Source `r12.0-p3s-test5`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test5)

## Test 4

Mounted the real ODM partition read-only to resolve the VINTF symlink loop.

Keystore2 registered and F2FS `/data` mounted. Device-encrypted key setup stopped at the missing fscrypt session keyring.

[Download Test 4](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test4) · [Source `r12.0-p3s-test4`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test4)

## Test 3

Extended the Keymaster registration deadline from five to 25 seconds.

Keymaster registered. Keystore2 hit the ODM VINTF symlink loop before `/data` could mount.

[Download Test 3](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test3) · [Source `r12.0-p3s-test3`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test3)

## Test 2

Added metadata and file-based decryption using existing storage keys.

Samsung Keymaster registered after about 13 seconds, past the five-second deadline. `/data` stayed unmounted.

[Download Test 2](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test2) · [Source `r12.0-p3s-test2`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test2)

## Test 1

Packaged the tested May-kernel baseline with a ramdisk small enough for the recovery partition.

Encrypted `/data` stayed unmounted.

[Download Test 1](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r12.0-p3s-test1) · [Source `r12.0-p3s-test1`](https://github.com/malick186/s21-ultra-fox-recovery/tree/r12.0-p3s-test1)
