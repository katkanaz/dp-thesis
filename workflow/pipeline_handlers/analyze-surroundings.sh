#!/bin/bash
#PBS -N analyze-surroundings
#PBS -l select=1:ncpus=4:mem=55gb
#PBS -l walltime=40:00:00


IFS="," read -r -a SUGARS <<< "$SUGAR_LIST"
IFS="," read -r -a RES_PATHS <<< "$RESULT_PATH_LIST"

SUGAR=${SUGARS[$PBS_ARRAY_INDEX]}
RES_PATH=${RES_PATHS[$PBS_ARRAY_INDEX]}

echo "$(date "+%Y-%m-%dT%H-%M") running analyze surroundings for sugar $SUGAR, saving result path to $RES_PATH" >> "$PIPELINE_RUN_LOG"

singularity exec -B $PDB_MIRROR_ROOT:/app/pdb-mirror -B $INIT_PQ:/app/init-pq-dir -B $PIPELINE_RUN:/app/workdir-volume workflow-singularity.sif bash -c "cd /app/src; python surrounding_analysis.py -s $SUGAR -a -c -d --store_result_path $RES_PATH"

RETURN_CODE="$?"
echo "$(date "+%Y-%m-%dT%H-%M") analysis for $SUGAR ended $RETURN_CODE" >> "$PIPELINE_RUN_LOG"
