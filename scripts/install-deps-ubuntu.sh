#!/usr/bin/env bash
set -e

apt=(sudo apt-get)
if [[ $(id -u) -eq 0 ]]; then
    apt=(apt-get)
fi

"${apt[@]}" -o Acquire::Retries=3 update
"${apt[@]}" -o Acquire::Retries=3 install -y --no-install-recommends \
    bc bison build-essential ca-certificates cpio curl file flex git git-lfs gnupg \
    gperf libelf-dev libncurses-dev libssl-dev libxml2-utils lz4 lzop openjdk-11-jdk \
    patch pngcrush python3 python-is-python3 rsync squashfs-tools unzip wget xsltproc \
    xz-utils zip zlib1g-dev
