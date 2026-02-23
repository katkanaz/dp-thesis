#!/bin/bash

set -e

if [ $# -ne 2 ]; then
	echo "Usage: $0 <SRC_DIR> <DEST_DIR>"
	exit 1
fi

SRC_DIR="$1"
DEST_DIR="$2"

mkdir -p "$DEST_DIR"

find "$SRC_DIR" -type f | while read -r file; do
	BASE=$(basename "$file")

	TARGET="$DEST_DIR/$BASE"

	ln -s "$(realpath --relative-to="$DEST_DIR" "$file")" "$TARGET"
done
