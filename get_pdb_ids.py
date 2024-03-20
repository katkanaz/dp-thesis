import csv
import json
from pathlib import Path
from collections import defaultdict

from csv import DictReader

DATA_FOLDER = Path(__file__).parent.parent / "data"
PATTERNS_FOLDER = Path(__file__).parent.parent / "pq_results" / "structures_with_sugars" / "patterns"

def get_pdb_ids_from_pq():
    """
    Gets PDB IDs of structures from PQ results.
    """
    structures = set()
    for i in PATTERNS_FOLDER.iterdir():
        structures.add(str(i.name).split("_")[0])
    with open((DATA_FOLDER / "pdb_ids_PQ.json"), "w") as f:
        json.dump(list(structures), f, indent=4)

if __name__ == "__main__":
    get_pdb_ids_from_pq()