#!/bin/bash
#PBS -N data-preprocessing
#PBS -l select=1:ncpus=4:mem=55gb
#PBS -l walltime=40:00:00


echo "$(date "+%Y-%m-%dT%H-%M") running data-preprocessing" >> "$PIPELINE_RUN_LOG"

docker run -it workflow bash -c "cd $PROJECT_ROOT/workflow/src; python data_preprocessing.py"
