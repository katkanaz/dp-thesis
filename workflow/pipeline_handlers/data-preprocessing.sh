#!/bin/bash
#PBS -N data-preprocessing
#PBS -l select=1:ncpus=4:mem=55gb
#PBS -l walltime=40:00:00


if [ $# -ne 2 ]; then
        echo "Usage: $0 <PROJECT_ROOT> <PIPELINE_RUN_LOG>"
        exit 1
fi


PROJECT_ROOT="$1"
PIPELINE_RUN_LOG="$2"


echo "$(date "+%Y-%m-%dT%H-%M") running data-preprocessing" >> "$PIPELINE_RUN_LOG"

docker run -it workflow bash -c "cd $PROJECT_ROOT/workflow/src; python data_preprocessing.py"
