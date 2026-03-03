#!/bin/bash
#PBS -N remove-outdated-symlinks
#PBS -l select=1:ncpus=1:mem=3gb
#PBS -l walltime=14:00:00


echo "$(date "+%Y-%m-%dT%H-%M") deleting outdated symlinks" >> "$PIPELINE_RUN_LOG"

rm -r "$PDB_MIRROR_ROOT/structures-files-delete"

rm -r "$PDB_MIRROR_ROOT/validation-files-delete" 
