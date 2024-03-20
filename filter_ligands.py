import json
from csv import DictReader
from pathlib import Path
from collections import defaultdict

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"

def filter_ligands(max_resolution, min_rscc, max_rmsd):
    """
    Filters ligands.json to contain only those structures whose overall resolution
    is better than <max_resolution> and residues with RSCC higher than <min_rscc>
    and rmsd lower than <max_rmsd>
    """
    with open(RESULTS_FOLDER / "categorization" / "ligands.json", "r") as f:
        ligands = json.load(f)
    print("number of structures before filtering: ", len(ligands.keys()))
    count = 0
    for pdb, residues in ligands.items():
        count += len(residues)
    print("number of residues before filtering: ", count)

    # save the pdb id of structures with good resolution, because not all structures have resolution
    # available and we want to continue just with those with resolution
    good_structures = set()
    with open(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if float(row["resolution"]) <= max_resolution and row["type"] == "ligand": 
                good_structures.add(row["pdb"])
    
    # delete those structures which are not in good_structures
    delete_strucutres = [pdb for pdb in ligands.keys() if pdb not in good_structures]
    for key in delete_strucutres: 
        del ligands[key]

    # get individual resiudes which have bad rscc or rmsd
    delete_residues = defaultdict(list)
    with open(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if row["type"] == "ligand" and (float(row["rmsd"]) > max_rmsd or float(row["rscc"]) < min_rscc):
                delete_residues[row["pdb"]].append({"name": row["name"], "num" : row["num"], "chain": row["chain"]}) 
    
    # save structures from which all residues were deleted
    delete_empty_structures = set()
    for pdb, residues in ligands.items():
        if pdb in delete_residues:
            for residue in delete_residues[pdb]:
                residues.remove(residue)
            if len(residues) == 0:
                delete_empty_structures.add(pdb)

    for key in delete_empty_structures:
        del ligands[key]

    print("number of structures after filtering: ", len(ligands.keys()))
    count = 0
    for pdb, residues in ligands.items():
        count += len(residues)
    print("number of residues after filtering: ", count)

    with open(RESULTS_FOLDER / "categorization" / "filtered_ligands.json", "w") as f:
        json.dump(ligands, f, indent=4)


if __name__ == "__main__":
    filter_ligands(3.0, 0.8, 2.0)