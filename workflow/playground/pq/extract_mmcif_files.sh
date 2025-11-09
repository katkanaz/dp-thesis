#!/bin/bash

cd pdb-mirror || exit

find . -mindepth 2 -type f -name "*.cif" -exec mv -i {} . \;

find . -mindepth 1 -type d -empty -delete
