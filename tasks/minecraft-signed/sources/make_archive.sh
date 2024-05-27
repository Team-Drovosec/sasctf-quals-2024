#!/bin/bash

SOURCE_DATE_EPOCH="2024-01-01"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pushd /Users/irdkwmnsb-mac/Downloads && gtar --sort=name \
     --mtime="${SOURCE_DATE_EPOCH}" \
     --owner=0 --group=0 --numeric-owner \
     --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
     -czf "$SCRIPT_DIR"/../static/signed.tar.gz signed && popd || return