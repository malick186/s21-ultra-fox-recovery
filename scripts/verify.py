#!/usr/bin/env python3
"""Check source checkout revisions and identify the packaged p3s recovery image."""

import argparse
import gzip
import hashlib
import struct
import xml.etree.ElementTree as ET
from pathlib import Path


def verify_platform(lock_path, manifest_path):
    expected = {
        (project.attrib["name"], project.attrib["path"]): project.attrib["revision"]
        for project in ET.parse(lock_path).getroot().findall("extend-project")
    }
    actual = {
        (project.attrib["name"], project.get("path", project.attrib["name"])): project.attrib["revision"]
        for project in ET.parse(manifest_path).getroot().findall("project")
        if project.get("path", project.attrib["name"]) != "bootable/recovery"
    }
    if not expected or expected != actual:
        different = sorted(key[1] for key in expected.keys() | actual.keys()
                           if expected.get(key) != actual.get(key))
        raise SystemExit(f"Android platform revision mismatch ({len(different)}): {', '.join(different[:10])}")
    print(f"Verified all {len(expected)} Android platform project revisions.")


def verify_crypto_ramdisk(ramdisk):
    required = {
        "prop.default",
        "system/bin/recovery",
        "system/bin/keystore2",
        "system/bin/vold_prepare_subdirs",
        "system/etc/init/keystore2.rc",
        "system/etc/init/p3s-recovery-crypto.rc",
        "system/lib64/android.hardware.gatekeeper@1.0.so",
        "system/lib64/android.hardware.keymaster@3.0.so",
        "system/lib64/android.hardware.keymaster@4.0.so",
        "system/lib64/android.hardware.keymaster@4.1.so",
        "vendor/etc/ueventd.rc",
        "vendor/etc/vintf/manifest.xml",
    }
    entries = {}
    offset = 0
    while offset + 110 <= len(ramdisk):
        if ramdisk[offset:offset + 6] not in (b"070701", b"070702"):
            raise SystemExit("Invalid CPIO entry in the recovery ramdisk.")
        size = int(ramdisk[offset + 54:offset + 62], 16)
        name_size = int(ramdisk[offset + 94:offset + 102], 16)
        name_end = offset + 110 + name_size
        data_start = (name_end + 3) & ~3
        data_end = data_start + size
        if name_size < 1 or data_end > len(ramdisk):
            raise SystemExit("Truncated CPIO entry in the recovery ramdisk.")
        name = ramdisk[offset + 110:name_end - 1].decode().removeprefix("./")
        if name == "TRAILER!!!":
            break
        if name in required:
            entries[name] = ramdisk[data_start:data_end]
        offset = (data_end + 3) & ~3

    if missing := required - entries.keys():
        raise SystemExit(f"Missing recovery crypto components: {', '.join(sorted(missing))}")
    recovery = entries["system/bin/recovery"]
    markers = (
        b"twrp.user.",
        b"Successfully decrypted metadata encrypted data partition",
        b"Unable to access existing metadata encryption keys",
        b"Samsung Keymaster 4.0 did not register in recovery",
        b"No existing file-encrypted user 0 key on /data",
    )
    if not all(marker in recovery for marker in markers):
        raise SystemExit("Recovery executable lacks the expected FBE or metadata decryption code.")
    manifest = ET.fromstring(entries["vendor/etc/vintf/manifest.xml"])
    hals = {hal.findtext("name"): hal for hal in manifest.findall("hal")}
    keymaster = hals.get("android.hardware.keymaster")
    if ("android.hardware.security.keymint" in hals or keymaster is None
            or keymaster.get("format") != "hidl"
            or keymaster.findtext("fqname") != "@4.0::IKeymasterDevice/default"):
        raise SystemExit("Recovery does not declare the expected Samsung vendor Keymaster interface.")
    init = entries["system/etc/init/p3s-recovery-crypto.rc"]
    if b"service p3s-tzdaemon " not in init or b"service p3s-keymaster " not in init:
        raise SystemExit("Recovery does not include the expected Samsung crypto startup services.")
    ueventd = entries["vendor/etc/ueventd.rc"]
    if not all(node in ueventd for node in (b"/dev/tzdev", b"/dev/tziwsock", b"/dev/tziwshmem")):
        raise SystemExit("Recovery does not include the Samsung TEEGRIS device permissions.")
    keystore_init = entries["system/etc/init/keystore2.rc"]
    if b"    disabled\n" not in keystore_init or b"    start keystore2\n" in keystore_init:
        raise SystemExit("Keystore2 is not gated on Samsung Keymaster readiness.")
    keystore = entries["system/bin/keystore2"]
    if (b"Recovery will not upgrade a storage key blob" not in keystore
            or b"Recovery will not upgrade a wrapped storage key blob" not in keystore):
        raise SystemExit("Recovery Keystore2 lacks the storage-key upgrade guard.")
    delete_keys_prop = b"ro.crypto.metadata_init_delete_all_keys.enabled="
    for prop in entries["prop.default"].splitlines():
        if prop.startswith(delete_keys_prop) and prop.removeprefix(delete_keys_prop).strip() not in (b"false", b"0"):
            raise SystemExit("Recovery enables metadata key deletion.")
    print("Verified recovery FBE and metadata decryption components.")


def verify_image(image_path, kernel_hash):
    image = image_path.read_bytes()
    if len(image) > 64 * 1024 ** 2:
        raise SystemExit("Recovery image exceeds the 64 MiB p3s partition limit.")
    if len(image) < 1652 or image[:8] != b"ANDROID!" or image[-16:] != b"SEANDROIDENFORCE":
        raise SystemExit("Unexpected boot image magic or Samsung footer.")

    kernel_size, ramdisk_size, page_size, version, dtbo_size, dtb_size = (
        struct.unpack_from("<I", image, offset)[0] for offset in (8, 16, 36, 40, 1632, 1648)
    )
    if (page_size, version) != (4096, 2) or min(kernel_size, ramdisk_size, dtbo_size, dtb_size) == 0:
        raise SystemExit("Unexpected p3s boot-image layout or missing payload.")
    ramdisk_offset = page_size + (kernel_size + page_size - 1) // page_size * page_size
    if ramdisk_offset + ramdisk_size > len(image) - 16:
        raise SystemExit("Recovery ramdisk extends beyond the image.")
    if hashlib.sha256(image[page_size:page_size + kernel_size]).hexdigest() != kernel_hash:
        raise SystemExit("Recovery image contains a different kernel.")
    ramdisk = gzip.decompress(image[ramdisk_offset:ramdisk_offset + ramdisk_size])
    if not ramdisk.startswith((b"070701", b"070702")) or b"R12.0" not in ramdisk:
        raise SystemExit("Expected an OrangeFox R12.0 CPIO ramdisk.")
    verify_crypto_ramdisk(ramdisk)
    print(f"Verified {len(image):,}-byte p3s recovery image and pinned kernel.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="check", required=True)
    platform = subparsers.add_parser("platform")
    platform.add_argument("lock", type=Path)
    platform.add_argument("manifest", type=Path)
    image = subparsers.add_parser("image")
    image.add_argument("recovery", type=Path)
    image.add_argument("kernel_sha256")
    args = parser.parse_args()
    if args.check == "platform":
        verify_platform(args.lock, args.manifest)
    else:
        verify_image(args.recovery, args.kernel_sha256)


if __name__ == "__main__":
    main()
