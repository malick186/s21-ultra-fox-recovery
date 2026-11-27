# Install S21 Ultra Fox Recovery R13 Stable

Use this recovery-only update on the **Galaxy S21 Ultra 5G Exynos SM-G998B (`p3s`)**. Start with an unlocked bootloader and an existing compatible custom recovery setup. Confirm the model in Download Mode. The verified configuration was an SM-G998B with bootloader `G998BXXSJHZC2` and a custom Android 17 ROM. Compatibility with other firmware and ROMs is unverified. Keep a copy of your files outside the phone and a known-working recovery package for your exact device.

## Verify the download

Get the recovery-only `.tar` for Odin, or the raw `-recovery.img` for an existing custom recovery. Compare the SHA-256 of the file you will flash to the matching row in the release's `.sha256` file. [R13 Stable downloads](https://github.com/malick186/s21-ultra-fox-recovery/releases/tag/r13.0-p3s-stable)

```powershell
Get-FileHash -Algorithm SHA256 .\S21-Ultra-Fox-Recovery-R13-Stable-p3s.tar
```

```bash
sha256sum -c S21-Ultra-Fox-Recovery-R13-Stable-p3s.sha256
```

The `sha256sum -c` command checks both downloads when both are in the same directory as the checksum file.

## Odin on Windows

1. Reboot the phone to Download Mode and connect it to the PC. Wait for Odin to detect the device.
2. Select the R13 `.tar` in **AP**. Leave **Auto Reboot** and **Re-Partition** unchecked. Keep BL, CP, CSC, and USERDATA empty.
3. Start the flash and wait for Odin to show **PASS**. With USB still connected, hold **Volume Down + Side key** until the screen goes black. Immediately switch to **Volume Up + Side key** to boot directly into recovery. [SM-G998B key sequence reference](https://github.com/afaneh92/android_device_samsung_p3s#download--guide)

## Existing TWRP or compatible recovery

Choose **Install Image**, select the verified R13 raw `.img`, choose **Recovery** as the destination, and confirm. Then reboot directly to **Recovery**. If the current recovery offers no Recovery destination, use the Odin method.

## Verify and roll back

Open recovery and enter your existing Android PIN locally if prompted. Check that Internal Storage opens. With ADB connected, `adb shell getprop twrp.user.0.decrypt` should report `1` after the primary user unlocks. If ADB is missing, reconnect USB and try toggling MTP from Mount.

If recovery boot or decryption fails, use Download Mode and flash your previous known-working SM-G998B recovery-only TAR in AP, then boot into that recovery. Preserve the existing data and encryption settings throughout the recovery update or rollback. Use the firmware vendor's own procedures for any separate bootloader or stock-firmware work.
