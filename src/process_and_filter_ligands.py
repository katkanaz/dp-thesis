from collections import defaultdict
from csv import DictReader
import json

from config import Config


def get_pdb_ids_with_rscc(config: Config) -> None:
    """
    Get the PDB IDs of structures whose residues have RSCC values

    :param config: Config object
    """

    with open(config.validation_results / "all_rscc_and_resolution.csv") as f:
        rscc = DictReader(f) #FIXME: Use pandas
        pdb_ids = set() #TODO: define elsewhere?
        for row in rscc:
            pdb_ids.add(row["pdb"])
    with open(config.validation_results / "pdbs_with_rscc_and_resolution.json", "w") as f:
        json.dump(list(pdb_ids), f, indent=4)


#NOTE: written specifically for previous work
#TODO: fix the 06
def remove_O6(config: Config) -> None:
    """
    Remove O6 atom of NAG, GAL, MAN, GLC and BGC from the structures

    :param config: Config object
    """

    with open(config.validation_results / "pdbs_with_rscc_and_resolution.json") as f:
        pdb_ids_of_interest = json.load(f)
    for pdb in pdb_ids_of_interest:
        with (config.mmcif_files / f"{pdb.lower()}.cif").open() as f:
            file = f.readlines()
        with (config.data_folder / "no_o6_mmcif" / f"{pdb.lower()}.cif").open("w") as f:
            for line in file:
                if line.startswith("HETATM"): #FIXME: Refactor if else
                    if "MAN" in line or "NAG" in line or "GAL" in line or "GLC" in line or "BGC" in line:
                        if "O6" in line:
                            continue
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                else:
                    f.write(line)


def filter_ligands(max_resolution: float, min_rscc: float, max_rmsd: float, config: Config) -> None:
    """
    Filter ligands.json to contain only the structures with overall resolution
    is better than <max_resolution> and residues with RSCC higher than <min_rscc>
    and rmsd lower than <max_rmsd>

    :param max_resolution: Maximal overall resolution
    :param min_rscc: Minimum RSCC of residue
    :param max_rmsd: Maximum RMSD of residue
    :param config: [TODO:description]
    """

    with open(config.categorization_results / "ligands.json", "r") as f:
        ligands = json.load(f)
    print("number of structures before filtering: ", len(ligands.keys()))
    count = 0
    for pdb, residues in ligands.items():
        count += len(residues)
    print("number of residues before filtering: ", count)

    # Save the pdb id of structures with good resolution, because not all structures have resolution
    # Available and we want to continue just with those with resolution
    good_structures = set()
    with open(config.validation_results / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if float(row["resolution"]) <= max_resolution and row["type"] == "ligand": 
                good_structures.add(row["pdb"])

    # Delete those structures which are not in good_structures
    delete_strucutres = [pdb for pdb in ligands.keys() if pdb not in good_structures]
    for key in delete_strucutres: 
        del ligands[key]

    # Get individual resiudes which have bad rscc or rmsd
    delete_residues = defaultdict(list)
    with open(config.validation_results / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if row["type"] == "ligand" and (float(row["rmsd"]) > max_rmsd or float(row["rscc"]) < min_rscc):
                delete_residues[row["pdb"]].append({"name": row["name"], "num" : row["num"], "chain": row["chain"]}) 

    # Save structures from which all residues were deleted
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

    with open(config.categorization_results / "filtered_ligands.json", "w") as f:
        json.dump(ligands, f, indent=4)


def process_and_filter_ligands(config: Config):

    get_pdb_ids_with_rscc(config)
    remove_O6(config)
    #TODO: Add argparse if necessary - are these values solid, is it based on literature? if yes then set as default
    filter_ligands(3.0, 0.8, 2.0, config)


if __name__ == "__main__":
    config = Config.load("config.json")

    (config.data_folder / "no_o6_mmcif").mkdir(exist_ok=True, parents=True)

    process_and_filter_ligands(config)
