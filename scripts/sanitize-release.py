#!/usr/bin/env python3
"""Strip the workstation hostname from the Galaxy S21 Ultra recovery packages."""

import argparse
import gzip
import hashlib
import io
import re
import struct
import tarfile
from pathlib import Path
from typing import NamedTuple


BUILD_HOST = b"build-host"
HOST_PROP = re.compile(rb"^ro\.build\.host=([^\r\n]+)(?=\r?$)", re.M)
SAMSUNG_FOOTER = b"SEANDROIDENFORCE"
BOOT_PAGE = 4096
PARTITION_SIZE = 64 * 1024 * 1024
BOOT_ID_OFFSET = 576
R13 = "S21-Ultra-Fox-Recovery-R13-Stable-p3s"


def align(size, alignment):
    return (size + alignment - 1) // alignment * alignment


def boot_id(payloads):
    digest = hashlib.sha1(usedforsecurity=False)
    for part in payloads:
        digest.update(part)
        digest.update(struct.pack("<I", len(part)))
    return digest.digest().ljust(32, b"\0")


def split_image(image):
    if not BOOT_PAGE < len(image) <= PARTITION_SIZE or image[:8] != b"ANDROID!":
        raise ValueError("unexpected recovery image size or magic")
    if image[-len(SAMSUNG_FOOTER):] != SAMSUNG_FOOTER:
        raise ValueError("missing Samsung recovery footer")
    page_size, version = struct.unpack_from("<2I", image, 36)
    if (page_size, version, struct.unpack_from("<I", image, 1644)[0]) != (BOOT_PAGE, 2, 1660):
        raise ValueError("expected a page-aligned Android boot v2 header")

    header = image[:BOOT_PAGE]
    sizes = [struct.unpack_from("<I", header, field)[0] for field in (8, 16, 24, 1632, 1648)]
    if any(sizes[index] == 0 for index in (0, 1, 3, 4)):
        raise ValueError("missing kernel, ramdisk, or device tree payload")
    offset = BOOT_PAGE
    payloads = []
    image_end = len(image) - len(SAMSUNG_FOOTER)
    for index, size in enumerate(sizes):
        if index == 3 and offset != struct.unpack_from("<Q", header, 1636)[0]:
            raise ValueError("invalid recovery DTBO offset")
        end = offset + size
        next_offset = align(end, BOOT_PAGE)
        if next_offset > image_end or any(image[end:next_offset]):
            raise ValueError("invalid recovery payload or padding")
        payloads.append(image[offset:end])
        offset = next_offset
    if offset != image_end or header[BOOT_ID_OFFSET:BOOT_ID_OFFSET + 32] != boot_id(payloads):
        raise ValueError("recovery image layout or boot ID is invalid")
    return header, payloads


class CpioEntry(NamedTuple):
    name: bytes
    start: int
    contents: int
    length: int
    end: int


def cpio_entries(data):
    offset = 0
    while offset + 110 <= len(data):
        header = data[offset:offset + 110]
        if header[:6] not in (b"070701", b"070702"):
            raise ValueError("invalid newc ramdisk header")
        size = int(header[54:62], 16)
        name_size = int(header[94:102], 16)
        name_start = offset + 110
        name_end = name_start + name_size
        contents = align(name_end, 4)
        end = align(contents + size, 4)
        if name_size < 1 or end > len(data) or data[name_end - 1] != 0:
            raise ValueError("invalid newc ramdisk entry")
        name = data[name_start:name_end - 1]
        yield CpioEntry(name, offset, contents, size, end)
        offset = end
        if name == b"TRAILER!!!":
            if size != 0 or any(data[offset:]):
                raise ValueError("unexpected data after ramdisk trailer")
            return
    raise ValueError("missing newc ramdisk trailer")


def scrub_ramdisk(ramdisk):
    original = list(cpio_entries(ramdisk))
    properties = [entry for entry in original if entry.name == b"prop.default"]
    if len(properties) != 1:
        raise ValueError("expected exactly one ramdisk prop.default")
    prop = properties[0]
    value = ramdisk[prop.contents:prop.contents + prop.length]
    hosts = list(HOST_PROP.finditer(value))
    if len(hosts) != 1:
        raise ValueError("expected exactly one ro.build.host property")
    old_host = hosts[0][1]
    if old_host == BUILD_HOST:
        return ramdisk, old_host

    new_value = HOST_PROP.sub(b"ro.build.host=" + BUILD_HOST, value)
    metadata = bytearray(ramdisk[prop.start:prop.contents])
    metadata[54:62] = f"{len(new_value):08x}".encode("ascii")
    if metadata[:6] == b"070702":
        metadata[102:110] = f"{sum(new_value) & 0xffffffff:08x}".encode("ascii")
    replacement = metadata + new_value + bytes(align(len(new_value), 4) - len(new_value))
    updated = ramdisk[:prop.start] + replacement + ramdisk[prop.end:original[-1].end]
    updated = updated.ljust(align(len(updated), 512), b"\0")
    if old_host.lower() in updated.lower():
        raise ValueError("original hostname occurs elsewhere in the ramdisk")

    revised = list(cpio_entries(updated))
    if [entry.name for entry in original] != [entry.name for entry in revised]:
        raise ValueError("sanitization changed the ramdisk file list")
    for before, after in zip(original, revised):
        if before == prop:
            if updated[after.start:after.end] != replacement:
                raise ValueError("rewritten prop.default differs from expected contents")
        elif ramdisk[before.start:before.end] != updated[after.start:after.end]:
            raise ValueError("sanitization changed an unrelated ramdisk entry")
    return updated, old_host


def sanitize_image(image):
    old_header, original = split_image(image)
    ramdisk, old_host = scrub_ramdisk(gzip.decompress(original[1]))
    if any(old_host.lower() in part.lower() for part in [old_header, *original[:1], *original[2:]]):
        raise ValueError("original hostname occurs outside the ramdisk")
    if old_host == BUILD_HOST:
        return image, old_host

    payloads = original.copy()
    payloads[1] = gzip.compress(ramdisk, compresslevel=9, mtime=0)
    header = bytearray(old_header)
    struct.pack_into("<I", header, 16, len(payloads[1]))
    struct.pack_into("<Q", header, 1636, BOOT_PAGE + sum(align(len(part), BOOT_PAGE)
                                                        for part in payloads[:3]))
    header[BOOT_ID_OFFSET:BOOT_ID_OFFSET + 32] = boot_id(payloads)
    updated = bytes(header) + b"".join(part.ljust(align(len(part), BOOT_PAGE), b"\0")
                                      for part in payloads) + SAMSUNG_FOOTER
    _, checked_parts = split_image(updated)
    if original[0] != checked_parts[0] or original[2:] != checked_parts[2:]:
        raise ValueError("sanitization changed a non-ramdisk boot segment")
    if gzip.decompress(checked_parts[1]) != ramdisk:
        raise ValueError("sanitized gzip does not contain the expected ramdisk")
    return updated, old_host


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_tar(archive, image):
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        entries = tar.getmembers()
        if len(entries) != 1 or entries[0].name != "recovery.img" or not entries[0].isfile():
            raise ValueError("expected an Odin TAR containing only recovery.img")
        member = tar.extractfile(entries[0])
        if member is None or member.read() != image:
            raise ValueError("Odin TAR recovery.img differs from the raw image")


def make_tar(image):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        member = tarfile.TarInfo("recovery.img")
        member.size = len(image)
        member.mode = 0o644
        tar.addfile(member, io.BytesIO(image))
    archive = stream.getvalue()
    verify_tar(archive, image)
    return archive


def checksum_records(entries):
    return "".join(f"{sha256(content)}  {name}\n" for name, content in entries.items()).encode("ascii")


def verify_checksums(directory, names, originals):
    recorded = {}
    for name in names:
        for line in (directory / name).read_text(encoding="ascii").splitlines():
            fields = line.split(maxsplit=1)
            if len(fields) != 2 or fields[1].lstrip("*") in recorded:
                raise ValueError("invalid original checksum record")
            recorded[fields[1].lstrip("*")] = fields[0]
    if recorded != {name: sha256(data) for name, data in originals.items()}:
        raise ValueError("original recovery or Odin TAR does not match its recorded checksum")


def write_exact(directory, name, data):
    path = directory / name
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"output differs from existing file {name}")
        return
    with path.open("xb") as output:
        output.write(data)


def write_package(directory, base, image_name, image, archive, sources):
    tar_name = f"{base}.tar"
    files = {tar_name: archive, image_name: image}
    if image_name == "recovery.img":
        write_exact(directory, f"{base}.sha256", checksum_records({tar_name: archive}))
        write_exact(directory, "recovery.img.sha256", checksum_records({image_name: image}))
    else:
        write_exact(directory, f"{base}.sha256", checksum_records(files))
    for name, data in files.items():
        write_exact(directory, name, data)
    write_exact(directory, f"{base}-sources.txt", sources)
    print(f"{base}: {len(image)} bytes, recovery {sha256(image)}, Odin TAR {sha256(archive)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("originals", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.resolve() == args.originals.resolve():
        parser.error("choose an output directory distinct from the original packages")
    args.output.mkdir(parents=True, exist_ok=True)
    for number in range(1, 12):
        suffix = "May-kernel" if number == 1 else f"Test{number}"
        base = f"OrangeFox-R12.0-Unofficial-p3s-{suffix}"
        tar_name = f"{base}.tar"
        image_name = "recovery.img" if number == 1 else f"{base}-recovery.img"
        checksum_names = [f"{base}.sha256"]
        if number == 1:
            checksum_names.append("recovery.img.sha256")
        image = (args.originals / image_name).read_bytes()
        archive = (args.originals / tar_name).read_bytes()
        verify_checksums(args.originals, checksum_names, {tar_name: archive, image_name: image})
        verify_tar(archive, image)
        clean_image, old_host = sanitize_image(image)
        clean_tar = make_tar(clean_image)
        sources = (args.originals / f"{base}-sources.txt").read_bytes()
        sources.decode("ascii")
        if (old_host != BUILD_HOST and old_host.lower() in sources.lower()
                or re.search(rb"[A-Za-z]:[\\/]Users[\\/]|/mnt/[a-z]/Users/|/home/|"
                             rb"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", sources, re.I)):
            raise ValueError("original build-input record contains private metadata")
        write_package(args.output, base, image_name, clean_image, clean_tar, sources)
        if number == 11:
            write_package(args.output, R13, f"{R13}-recovery.img", clean_image, clean_tar, sources)


if __name__ == "__main__":
    main()
