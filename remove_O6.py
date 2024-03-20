from csv import DictReader
import json
from pathlib import Path


RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
DATA_FOLDER = Path("/Volumes/YangYang/diplomka") / "data"


def get_pdb_ids_with_rscc():
    """
    Get PDB IDs of structures for which residues there are the RSCC values.
    """
    with open(RESULTS_FOLDER / "validation" / "all_rscc_and_resolution.csv") as f:
        rscc = DictReader(f) # TODO: maybe use pandas
        pdb_ids = set()
        for row in rscc:
            pdb_ids.add(row["pdb"])
    with open(RESULTS_FOLDER / "validation" / "pdbs_with_rscc_and_resolution.json", "w") as f:
        json.dump(list(pdb_ids), f, indent=4)


def remove_O6():
    """
    Removes atom O6 of NAG, GAL, MAN, GLC and BGC from the structures.
    """
    result = DATA_FOLDER / "mmCIF_without_O6"
    result.mkdir(exist_ok=True)
    with open(RESULTS_FOLDER / "validation" / "pdbs_with_rscc_and_resolution.json") as f:
        pdb_ids_of_interest = json.load(f)
    for pdb in pdb_ids_of_interest:
        with (DATA_FOLDER / "mmCIF_files"/ f"{pdb.lower()}.cif").open() as f:
            file = f.readlines()
        with (result / f"{pdb.lower()}.cif").open("w") as f:
            for line in file:
                if line.startswith("HETATM"):
                    if "MAN" in line or "NAG" in line or "GAL" in line or "GLC" in line or "BGC" in line:
                        if "O6" in line:
                            continue
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                else:
                    f.write(line)


if __name__ == "__main__":
    remove_O6()