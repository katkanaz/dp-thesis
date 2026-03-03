#!/bin/bash
#PBS -N init-pq
#PBS -l select=1:ncpus=4:mem=55gb:scratch_ssd=90gb
#PBS -l walltime=40:00:00 


RUNDATE=$(date "+%Y-%m-%dT%H-%M")


test -n "$SCRATCHDIR" || { echo >&2 "Variable SCRATCHDIR is not set!"; exit 2; }

echo "$(date "+%Y-%m-%dT%H-%M") starting PDB mirror copy for PQ" >> "$PIPELINE_RUN_LOG"
echo "Using scratchdir: $SCRATCHDIR" > "$PIPELINE_RUN/pq_run.log"

cp -r "$PDB_MIRROR_ROOT/structures-files" "$SCRATCHDIR/structures-files"

module add mono

cat <<EOF > $PIPELINE_RUN/pq-config.json
{
        "InputFolders": [
           "$SCRATCHDIR/structures-files"
        ],
        "Queries": [
            {
                "Id": "structures-with-sugars",
                "QueryString": "Or(AtomNames('C3').Inside(Rings(4*['C']+['O'])), AtomNames('C4').Inside(Rings(4*['C']+['O'])), AtomNames('C3').Inside(Rings(5*['C']+['O'])), AtomNames('C4').Inside(Rings(5*['C']+['O']))).Filter(lambda a:a.IsConnectedTo(Atoms('O')))"
            }
        ],
        "StatisticsOnly": false,
        "MaxParallelism": 2
}
EOF

mono PatternQuery_1.1.23.12.27b/WebChemistry.Queries.Service.exe "$PIPELINE_RUN/pq-results" "$PIPELINE_RUN/pq-config.json" >> "$PIPELINE_RUN/pq_run.log"

cp "$PIPELINE_RUN/pq-results/result.zip" "$INIT_PQ/result.zip"

clean_scratch

