"""
Script Name: alternative_conformations.py
Description: Create separate mmCIF files for alternative sugar conformations
Author: Kateřina Nazarčuková
"""


from enum import Enum
import json
import gemmi
from pathlib import Path
from typing import List, Dict, Tuple

from logger import logger, setup_logger
from configuration import Config


class AltlocCase(Enum):
    SINGLE_RES = 1
    DOUBLE_RES = 2

class AltlocError(Exception):
    def __init__(self, filename, message="Too many types of altlocs") -> None:
        self.filename = filename
        self.message = message
        super().__init__(f"{message} in file {filename}")

    def __str__(self) -> str:
        return f"{self.message} in file: {self.filename}"


#TODO: Refactor global varible
files_with_altlocs = 0


def delete_alternative_conformations(structure: gemmi.Structure, residues_to_keep: List[Dict], residues_to_delete: List[Dict]) -> None:
    """
    Delete unwanted alternative conformations of a structure and set the ones that should be kept to "\0"

    :param structure: Structure in question
    :param residues_to_keep: List of residues whose altlocs should be set to "\0"
    :param residues_to_delete: List of residues to delete in the given structure
    """
    for residue in residues_to_keep:
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        for atom in structure[model_idx][chain_idx][residue_idx]:
            atom.altloc = "\0"

    for residue in reversed(residues_to_delete):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure[model_idx][chain_idx][residue_idx]
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc_del"]):
                del structure[model_idx][chain_idx][residue_idx][atom_idx]


# TODO: Add docs
def save_files(structure: gemmi.Structure, input_file: Path, conformation_type: str) -> None:
    #FIXME: Options don't work for atom and hetatm lines
    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    new_path = Path("../tmp/alter_conform/test_july_data_after_dictsol/") / f"{conformation_type}_{input_file.name}" #TODO: fix using config, save to modified mmcifs
    structure.make_mmcif_document().write_file(str(new_path), options)


# TODO: Add docs
def separate_alternative_conformations(input_file: Path) -> bool:
    with open("../tmp/alter_conform/sugar_names.json") as f: #TODO: fix using config 
        sugar_names = set(json.load(f)) # Set for optimalization

    global files_with_altlocs

    structure_a = gemmi.read_structure(str(input_file))

    # Lists of alternative conformations
    altloc_a: List[Dict] = []
    altloc_b: List[Dict] = []

    # Remember seen residues
    residues: Dict[Tuple[str, gemmi.SeqId, str], Tuple[str, str]] = {}

    models_count = 0
    for model_idx, model in enumerate(structure_a):
        models_count += 1
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                if residue.name in sugar_names:
                    print(f"res {residue.name}, num {residue.seqid}, altloc {type(residue[0].altloc)}, chain {chain.name}")
                    atom_altloc_a = []
                    atom_altloc_b = []

                    #FIXME:
                    # NOTE: Can one be sure, one atom won't have a altloc missing
                    # if residue[0].altloc == "\0":
                    #     continue

                    first_altloc_key = None
                    second_altloc_key = None

                    for atom_idx, atom in enumerate(residue):
                        if atom.altloc != "\0":
                            key = (residue.name, residue.seqid, atom.altloc)
                            if first_altloc_key is None and key not in residues:
                                first_altloc_key = atom.altloc
                                residues[key] = (first_altloc_key, chain.name)
                                # print(f"first key is {first_altloc_key}")
                            elif atom.altloc != first_altloc_key and second_altloc_key is None:
                                if key in residues and residues[key] == atom.altloc:
                                    raise AltlocError(input_file.name, "Previously seen residue has same altloc!") 
                                second_altloc_key = atom.altloc
                                # print(f"second key is {second_altloc_key}")
                                
                            elif atom.altloc != first_altloc_key and atom.altloc != second_altloc_key:
                                #TODO: function here ends, file is removed, ask Pepa
                                raise AltlocError(input_file.name)
                                print(f"File {input_file.name} has more than 2 tpyes of altlocs!")


                            if atom.altloc == first_altloc_key:
                                atom_altloc_a.append(atom_idx)
                                # print(f"A is {atom_altloc_a}")
                                # print(first_altloc_key)
                            elif atom.altloc == second_altloc_key:
                                atom_altloc_b.append(atom_idx)
                                # print(f"B is {atom_altloc_b}")
                                # print(second_altloc_key)

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
                        res_a = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_a}
                        # print(res_a)
                        altloc_a.append(res_a)
                        res_b = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_b}
                        altloc_b.append(res_b)
                        # print(res_b)
                    elif atom_altloc_a or atom_altloc_b:
                        altloc_case = AltlocCase.DOUBLE_RES
                        res = {**common_values, "altloc_case": altloc_case}
                        list_to_append_to = altloc_a if atom_altloc_a else altloc_b
                        list_to_append_to.append(res)


    if models_count > 1:
        print(f"More than one model in: {input_file.name}") #NOTE: Learn if normal

    if not altloc_a and not altloc_b:
        return False

    # if bool(altloc_a) != bool(altloc_b):
    #     print(f"{input_file.name}")

    if altloc_a:
    # File with only A conformers
    # print(altloc_a)
        delete_alternative_conformations(structure_a, altloc_a, altloc_b)
        save_files(structure_a, input_file, "A")

    if altloc_b:
    # File with only B conformers
    # print(altloc_b)
        structure_b = gemmi.read_structure(str(input_file))
        delete_alternative_conformations(structure_b, altloc_b, altloc_a)
        save_files(structure_b, input_file, "B")

    files_with_altlocs += 1
    return True

# TODO: Change to main
def create_separate_mmcifs() -> None:
    #TODO: Add modified mmcif folder creation here plus to config
    # with open("../results/ligand_sort/july_2024/categorization/ligands.json", "r") as f: #TODO: change using config
    #     only_ligands: Dict = json.load(f)

    # ids = [id.lower() for id in only_ligands.keys()]
    # for file in sorted(Path("../data/july_2024/mmcif_files").glob("*.cif")): #TODO: Add config, load mmcif files, return true for altloc or false, if flase copy to modifiedmmcif
    #     if file.stem in ids:
    #         try:
    #             separate_alternative_conformations(file)
    #         except AltlocError as e:
    #             print(f"Exception caught: {e}")
    # print(f"Number of files with altlocs: {files_with_altlocs}")
    try:
        separate_alternative_conformations(Path("../data/july_2024/mmcif_files/2y9g.cif"))
    except AltlocError as e:
        print(f"Exception caught: {e}")
    
if __name__ == "__main__":
    # config = Config.load("config.json", None, False)
    #
    # setup_logger(config.log_path)
    
    create_separate_mmcifs()
#TODO: setup config and logger
