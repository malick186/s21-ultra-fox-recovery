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
