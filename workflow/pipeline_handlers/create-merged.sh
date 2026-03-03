#!/bin/bash
#PBS -N create-merged-results
#PBS -l select=1:ncpus=1:mem=55gb
#PBS -l walltime=2:00:00


IFS="," read -r -a RES_PATHS <<< "$RESULT_PATH_LIST"

SOURCE_ARGS_LIST=""
for RES_PATH in "${RES_PATHS[@]}"; do
        SOURCE_ARGS_LIST="$SOURCE_ARGS_LIST -s $RES_PATH"
done

echo "$(date "+%Y-%m-%dT%H-%M") creating merged results" >> "$PIPELINE_RUN_LOG"

docker run -it workflow bash -c "cd $PROJECT_ROOT/workflow/src; python create_merged_results.py $SOURCE_ARGS_LIST -o $output" #TODO: mount volumes to docker
