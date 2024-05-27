#!/bin/bash

SOURCE_DATE_EPOCH="2024-01-01"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pushd "/Users/irdkwmnsb-mac/Library/Application Support/PrismLauncher/instances/1.20.4/.minecraft/saves/minotaur" && ls . && gtar --sort=name \
     --mtime="${SOURCE_DATE_EPOCH}" \
     --owner=0 --group=0 --numeric-owner \
     --no-same-owner --no-same-permissions \
     --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
     -czf "$SCRIPT_DIR"/../server/server/world.tar.gz . && popd || return

tar -ztvf "$SCRIPT_DIR"/../server/server/world.tar.gz