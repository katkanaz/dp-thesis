#!/bin/bash

SEARCH_DIR="$1"

OUTPUT="matched_files.txt"
# > "$OUTPUT"

COUNT=0

[ -d "$SEARCH_DIR" ] || { echo "Directory not found: $SEARCH_DIR"; exit 1; }

for file in "$SEARCH_DIR"; do
    [ -f "$file" ] || continue
    
    first_line=$(head -n 1 "$file")

    if [[ $first_line == END* ]]; then
        echo "$file" >> "$OUTPUT"
        ((COUNT++))
    fi
done

echo "Number of files starting with 'END': $COUNT"
