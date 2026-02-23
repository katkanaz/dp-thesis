#!/bin/bash
#PBS -N create-merged-results
#PBS -l select=1:ncpus=1:mem=55gb
#PBS -l walltime=2:00:00


if [ $# -ne 4 ]; then
        echo "Usage: $0 <PROJECT_ROOT> <PIPELINE_RUN_LOG> <RESULT_PATH_LIST> <OUTPUT>"
        exit 1
fi


PROJECT_ROOT="$1"
PIPELINE_RUN_LOG="$2"
RESULT_PATH_LIST="$3"
OUTPUT="$4"

IFS="," read -r -a RES_PATHS <<< "$RESULT_PATH_LIST"

SOURCE_ARGS_LIST=""
for RES_PATH in "${RES_PATHS[@]}"; do
        SOURCE_ARGS_LIST="$SOURCE_ARGS_LIST -s $RES_PATH"
done

echo "$(date "+%Y-%m-%dT%H-%M") creating merged results" >> "$PIPELINE_RUN_LOG"

docker run -it workflow bash -c "cd $PROJECT_ROOT/workflow/src; python create_merged_results.py $SOURCE_ARGS_LIST -o $output" #TODO: mount volumes to docker
