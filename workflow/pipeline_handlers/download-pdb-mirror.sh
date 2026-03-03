#!/bin/bash
#PBS -N download-pdb-mirror
#PBS -l select=1:ncpus=1:mem=16gb
#PBS -l walltime=14:00:00


RUNDATE=$(date "+%Y-%m-%dT%H-%M")

if [[ $PBS_ARRAY_INDEX -eq 0 ]]; then
	echo "$RUNDATE In download-pdb-mirror, index $PBS_ARRAY_INDEX, parent: $PBS_ARRAY_ID" >> "$PIPELINE_RUN_LOG"
	rsync -rlpt -v -z --delete --info=progress2 --port=33444 rsync.rcsb.org::ftp_data/structures/divided/mmCIF/ "$PDB_MIRROR_ROOT/structures-download" > "$PIPELINE_RUN/download_structures.log"

	if [[ -d "$PDB_MIRROR_ROOT/structures-files" ]]; then
		mv "$PDB_MIRROR_ROOT/structures-files" "$PDB_MIRROR_ROOT/structures-files-delete"
	fi

	"$PROJECT_ROOT/workflow/pipeline-handlers/flatten-directory.sh" "$PDB_MIRROR_ROOT/structures-download" "$PDB_MIRROR_ROOT/structures-files"
else
	echo "$RUNDATE In download-pdb-mirror, index $PBS_ARRAY_INDEX, parent: $PBS_ARRAY_ID" >> "$PIPELINE_RUN_LOG"
	rsync -rlpt -v -z --delete --include="*/" --include="*.xml.gz" --exclude="*" --info=progress2 --port=33444 rsync.rcsb.org::ftp/validation_reports/ "$PDB_MIRROR_ROOT/validation-download" > "$PIPELINE_RUN/download_validation_files.log"

	if [[ -d "$PDB_MIRROR_ROOT/validation-files" ]]; then
		mv "$PDB_MIRROR_ROOT/validation-files" "$PDB_MIRROR_ROOT/validation-files-delete"
	fi

	"$PROJECT_ROOT/workflow/pipeline-handlers/flatten-directory.sh" "$PDB_MIRROR_ROOT/validation-download" "$PDB_MIRROR_ROOT/validation-files"
fi
