#!/bin/bash
#PBS -N data-preprocessing
#PBS -l select=1:ncpus=4:mem=55gb
#PBS -l walltime=40:00:00


echo "$(date "+%Y-%m-%dT%H-%M") running data-preprocessing" >> "$PIPELINE_RUN_LOG"

singularity exec -B $PDB_MIRROR_ROOT:/app/pdb-mirror -B $INIT_PQ:/app/init-pq-dir -B $PIPELINE_RUN:/app/workdir-volume workflow-singularity.sif bash -c "cd /app/src; python data_preprocessing.py"
