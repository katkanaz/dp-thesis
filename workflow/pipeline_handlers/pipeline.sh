#!/bin/bash
if [ $# -ne 5 ]; then
        echo "Usage: $0 <PROJECT_ROOT> <PIPELINE_RUNS_ROOT> <PDB_MIRROR_ROOT> <SUGAR_LIST> <OUTPUT_DIR>"
        exit 1
fi


PROJECT_ROOT="$1"
PIPELINE_RUNS_ROOT="$2"
PDB_MIRROR_ROOT="$3"
SUGAR_LIST="$4"
OUTPUT_DIR="$5"

IFS="," read -r -a SUGARS <<< "$SUGAR_LIST"
LAST_SUGAR_IDX=$((${#SUGARS[@]} - 1))

RESULT_PATH_LIST=""
for SUGAR in "${SUGARS[@]}"; do
	RESULT_PATH_LIST="$RESULT_PATH_LIST,$PIPELINE_RUNS_ROOT/$SUGAR-res"
done

PIPELINE_RUN="$PIPELINE_RUNS_ROOT/$(date "+%Y-%m-%dT%H-%M")"
mkdir "$PIPELINE_RUN" || exit 2

PIPELINE_RUN_LOG="$PIPELINE_RUN/pipeline.log"
echo "$(date "+%Y-%m-%dT%H-%M") beginning pipeline" > "$PIPELINE_RUN_LOG"

DOWNLOAD_ID=$(qsub -J 0-1 -F "$PROJECT_ROOT $PIPELINE_RUN $PIPELINE_RUN_LOG $PDB_MIRROR_ROOT" download-pdb-mirror.sh)
echo "Creating download job: $DOWNLOAD_ID" >> "$PIPELINE_RUN_LOG"

INIT_PQ_ID=$(qsub -W depend=afterok:"$DOWNLOAD_ID" -F "$PIPELINE_RUN $PIPELINE_RUN_LOG $PDB_MIRROR_ROOT" init-pq-run.sh) #TODO: handle zip
echo "Creating initial PQ job: $INIT_PQ_ID" >> "$PIPELINE_RUN_LOG"

REMOVE_LINKS_ID=$(qsub -W depend=afterok:"$DOWNLOAD_ID" -F "$PIPELINE_RUN_LOG $PDB_MIRROR_ROOT" remove-outdated-symlinks.sh)
echo "Creating remove links job: $REMOVE_LINKS_ID" >> "$PIPELINE_RUN_LOG"

DATA_PREPROCESS_ID=$(qsub -W depend=afterok:"$INIT_PQ_ID" -F "$PROJECT_ROOT $PIPELINE_RUN_LOG" data-preprocessing.sh)
echo "Creating data pre-processing job: $DATA_PREPROCESS_ID" >> "$PIPELINE_RUN_LOG"

ANALYZE_SURROUNDINGS_ID=$(qsub -J 0-$LAST_SUGAR_IDX -W depend=afterok:"$DATA_PREPROCESS_ID" -F "$PROJECT_ROOT $PIPELINE_RUN_LOG $SUGAR_LIST $RESULT_PATH_LIST" analyze-surroundings.sh)
echo "Creating analyze surroundings job: $ANALYZE_SURROUNDINGS_ID" >> "$PIPELINE_RUN_LOG"

CREATE_MERGED_ID=$(qsub -W depend=afterok:"$ANALYZE_SURROUNDINGS_ID" -F "$PROJECT_ROOT $PIPELINE_RUN_LOG $RESULT_PATH_LIST $OUTPUT" create-merged.sh) #TODO: output je output dir, jmeno souboru s data kdy spustena pipeline
echo "Creating merged results job: $CREATE_MERGED_ID" >> "$PIPELINE_RUN_LOG"
