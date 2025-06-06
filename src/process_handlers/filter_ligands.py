"""
Script Name: filter_ligands.py
Description: Filter modified_ligands.json based on given criteria of quality.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from collections import defaultdict
from csv import DictReader
import json
from logger import logger, setup_logger
from typing import Dict

from configuration import Config
from utils.hide_altloc import remove_altloc_from_id


#TODO: Add docs
def count_num_residues(res_in_whole_struct: Dict) -> int:
    return sum([len(residues) for residues in res_in_whole_struct.values()])


def filter_ligands(max_resolution: float, min_rscc: float, max_rmsd: float, config: Config) -> None:
    # TODO: Explain default values origin
    """
    Filter ligands.json to contain only the structures with overall resolution
    is better than <max_resolution> and residues with RSCC higher than <min_rscc>
    and rmsd lower than <max_rmsd>

    :param max_resolution: Maximal overall resolution
    :param min_rscc: Minimum RSCC of residue
    :param max_rmsd: Maximum RMSD of residue
    :param config: Config object
    """

    with open(config.categorization_dir / "modified_ligands.json", "r", encoding="utf8") as f:
        modified_ligands = json.load(f)

    # FIXME: These numbers can be missleading since the structures with alternative conformations are now split into two
    logger.info(f"Number of structures before filtering: {len(modified_ligands.keys())}")
    logger.info(f"Number of residues before filtering: {count_num_residues(modified_ligands)}")

    # Save the pdb id of structures with good resolution, because not all structures have resolution
    # Available and we want to continue just with those with resolution
    good_structures = set()
    # Get individual resiudes which have bad rscc or rmsd
    delete_residues = defaultdict(list)
    with open(config.validation_dir / "merged_rscc_rmsd.csv", "r", encoding="utf8") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if float(row["resolution"]) <= max_resolution and row["type"] == "ligand":
                good_structures.add(row["pdb"])
            if row["type"] == "ligand" and (float(row["rmsd"]) > max_rmsd or float(row["rscc"]) < min_rscc):
                delete_residues[row["pdb"]].append({"name": row["name"], "num" : row["num"], "chain": row["chain"]}) 

    # Delete those structures which are not in good_structures
    delete_structures = set([pdb for pdb in modified_ligands.keys() if remove_altloc_from_id(pdb) not in good_structures])
    for key in delete_structures:
        del modified_ligands[key]

    # Get individual resiudes which have bad rscc or rmsd
    # delete_residues = defaultdict(list)
    # with open(config.validation_dir / "merged_rscc_rmsd.csv", "r", encoding="utf8") as f: # FIXME: Delete this after testing
        # rscc_rmsd = DictReader(f)
        # for row in rscc_rmsd:
        #     if row["type"] == "ligand" and (float(row["rmsd"]) > max_rmsd or float(row["rscc"]) < min_rscc):
        #         delete_residues[row["pdb"]].append({"name": row["name"], "num" : row["num"], "chain": row["chain"]}) 

    # Save structures from which all residues were deleted
    delete_empty_structures = set()
    for pdb, residues in modified_ligands.items():# FIXME: Is it necessary to iterate over the same dict twice?
        if remove_altloc_from_id(pdb) in delete_residues:
            for residue in delete_residues[remove_altloc_from_id(pdb)]:
                try:
                    residues.remove(residue)
                except ValueError as e:
                    pass # Some residues to delete might already not be there due to altloc split

            if len(residues) == 0:
                delete_empty_structures.add(pdb)

    for key in delete_empty_structures:
        del modified_ligands[key]

    logger.info(f"Number of structures after filtering: {len(modified_ligands.keys())}")
    logger.info(f"Number of residues after filtering: {count_num_residues(modified_ligands)}")

    with open(config.categorization_dir / "filtered_modified_ligands.json", "w", encoding="utf8") as f:
        json.dump(modified_ligands, f, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--res", help="Value of maximum overall resolution of structure",
                        type="float", default=3.0)
    parser.add_argument("--rscc", help="Value of minimum RSCC of residue",
                        type="float", default=0.8)
    parser.add_argument("--rmsd", help="Value of maximum RMSD of residue",
                        type="float", default=2.0)

    args = parser.parse_args()

    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    filter_ligands(args.res, args.rscc, args.rmsd, config)

    Config.clear_current_run()
