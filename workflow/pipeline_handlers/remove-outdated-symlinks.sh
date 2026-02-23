#!/bin/bash
#PBS -N remove-outdated-symlinks
#PBS -l select=1:ncpus=1:mem=3gb
#PBS -l walltime=14:00:00


if [ $# -ne 2 ]; then
        echo "Usage: $0 <PIPELINE_RUN_LOG> <PDB_MIRROR_ROOT>"
        exit 1
fi


PIPELINE_RUN_LOG="$1"
PDB_MIRROR_ROOT="$2"


echo "$(date "+%Y-%m-%dT%H-%M") deleting outdated symlinks" >> "$PIPELINE_RUN_LOG"

rm -r "$PDB_MIRROR_ROOT/structures-files-delete"

rm -r "$PDB_MIRROR_ROOT/validation-files-delete" 
