"""
Script Name: alternate_conformations.py
Description: Create separate mmCIF files for alternate sugar conformations
Author: Kateřina Nazarčuková
"""


from enum import Enum
import json
import gemmi
from pathlib import Path
from typing import List, Dict

from logger import logger, setup_logger
from configuration import Config


class AltlocCase(Enum):
    SINGLE_RES = 1
    DOUBLE_RES = 2


files_with_altlocs = 0

def delete_alternate_conformations() -> None:
    pass

# TODO: Add docs
def separate_alternate_conformations(input_file: Path) -> None:
    with open("../tmp/alter_conform/sugar_names.json") as f: 
        sugar_names = set(json.load(f)) # Set for optimalization

    global files_with_altlocs

    structure_a = gemmi.read_structure(str(input_file)) # TODO: Load mmcif file from data directory

    altloc_a: List[Dict] = []
    altloc_b: List[Dict] = []

    models_count = 0
    for model_idx, model in enumerate(structure_a):
        models_count += 1
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                if residue.name in sugar_names:
                    atom_altloc_a = []
                    atom_altloc_b = []

                    # NOTE: Can one be sure, one atom won't have a altloc missing
                    # if residue[0].altloc == "\0":
                    #     continue

                    first_altloc_key = None
                    second_altloc_key = None

                    for atom_idx, atom in enumerate(residue):
                        if atom.altloc != "\0":
                            if first_altloc_key is None:
                                first_altloc_key = atom.altloc
                            elif atom.altloc != first_altloc_key and second_altloc_key is None:
                                second_altloc_key = atom.altloc

                            if atom.altloc == first_altloc_key:
                                atom_altloc_a.append(atom_idx)
                            elif atom.altloc == second_altloc_key:
                                atom_altloc_b.append(atom_idx)

                    if not atom_altloc_a and not atom_altloc_b:
                        # Both lists are empty, residue has no alternate conformations
                        continue

                    common_values = {
                        "model_idx": model_idx,
                        "chain_idx": chain_idx,
                        "residue_idx": residue_idx,
                        "residue_name": residue.name
                    }

                    if atom_altloc_a and atom_altloc_b:
                        if len(atom_altloc_a) != len(atom_altloc_b):
                            print(f"Not the same number of atoms in each conformation: {input_file.name}")
                        altloc_case = AltlocCase.SINGLE_RES
                        res_a = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_a, "atom_altloc_keep": atom_altloc_b}
                        altloc_a.append(res_a)
                        res_b = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_b, "atom_altloc_keep": atom_altloc_a}
                        altloc_b.append(res_b)
                    elif atom_altloc_a or atom_altloc_b:
                        altloc_case = AltlocCase.DOUBLE_RES
                        res = {**common_values, "altloc_case": altloc_case}
                        list_to_append_to = altloc_a if atom_altloc_a else altloc_b
                        list_to_append_to.append(res)


    if altloc_a:
        files_with_altlocs += 1
    # TODO: Extract to function

    # for atom_idx in residue["atom_altloc_keep"]:
    #     structure_b[model_idx][chain_idx][residue_idx][atom_idx].altloc = "\0"
    # File with only B conformers
    structure_b = gemmi.read_structure(str(input_file))

    for residue in altloc_b:
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        for atom in structure_b[model_idx][chain_idx][residue_idx]:
            atom.altloc = "\0"

    for residue in reversed(altloc_a):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure_b[model_idx][chain_idx][residue_idx]
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc_del"]):
                del structure_b[model_idx][chain_idx][residue_idx][atom_idx]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    # TODO: Save to file
    new_path = Path("../tmp/alter_conform/test_july_data_5/") / f"B_{input_file.name}"
    structure_b.make_mmcif_document().write_file(str(new_path), options)

    # File with only A conformers
    # for atom_idx in residue["atom_altloc_keep"]:
    #     structure_a[model_idx][chain_idx][residue_idx][atom_idx].altloc = "\0"

    for residue in altloc_a:
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        for atom in structure_a[model_idx][chain_idx][residue_idx]:
            atom.altloc = "\0"

    for residue in reversed(altloc_b):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure_a[model_idx][chain_idx][residue_idx]
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc_del"]):
                del structure_a[model_idx][chain_idx][residue_idx][atom_idx]

    # TODO: Save to file
    new_path_a = Path("../tmp/alter_conform/test_july_data_5/")/ f"A_{input_file.name}"
    structure_a.make_mmcif_document().write_file(str(new_path_a), options)

    if models_count > 1:
        print(f"More than one model in: {input_file.name}")


# NOTE: Only with files that have ligands
# TODO: Change to main
def create_separate_mmcifs() -> None:
    with open("../results/ligand_sort/july_2024/categorization/ligands.json", "r") as f:
        only_ligands: Dict = json.load(f)

    ids = [id.lower() for id in only_ligands.keys()]
    for file in sorted(Path("../data/july_2024/mmcif_files").glob("*.cif")):
        if file.stem in ids:
            separate_alternate_conformations(file)
    print(f"Number of files with altlocs: {files_with_altlocs}")
    
if __name__ == "__main__":
    # config = Config.load("config.json", None, False)
    #
    # setup_logger(config.log_path)
    
    create_separate_mmcifs()

