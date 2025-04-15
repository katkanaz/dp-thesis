"""
Script Name: alternative_conformations.py
Description: Create separate mmCIF files for alternative sugar conformations
Author: Kateřina Nazarčuková
"""


from enum import Enum
import json
import gemmi
from pathlib import Path
from typing import List, Dict
from shutil import copy2

from logger import logger, setup_logger
from configuration import Config


class AltlocCase(Enum):
    SINGLE_RES = 1
    DOUBLE_RES = 2

class AltlocError(Exception):
    def __init__(self, filename, altloc, message="Not supported altloc type") -> None:
        self.filename = filename
        self.altloc = altloc
        self.message = message
        super().__init__(f"{message} {altloc} in file {filename}")

    def __str__(self) -> str:
        return f"{self.message} of {self.altloc} in file: {self.filename}"

class AltlocKind(Enum):
    NO_ALTLOC = 1 # Files with no alternative conformations
    NORMAL_ALTLOC = 2 # Files with both A and B altlocs 
    SINGLE_KIND_ALTLOC = 3 # Files with only A or B altlocs


def delete_alternative_conformations(structure: gemmi.Structure, residues_to_keep: List[Dict], residues_to_delete: List[Dict], ligand_values: List[Tuple[str, str, str]]) -> List[Dict]:
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


    new_values: Set[Tuple[str, str, str]] = set(ligand_values)
    if len(new_values) != len(ligand_values):
        logger.warning(f"Ligand values contains duplicates {new_values=} {ligand_values=}")
    for residue in reversed(residues_to_delete):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure[model_idx][chain_idx][residue_idx]
            res_tuple = (residue["residue_name"], residue["residue_num"], residue["residue_chain"])
            if res_tuple in new_values:
                new_values.remove(res_tuple)
            else:
                logger.warning(f"res_str {res_tuple} not in new_values")
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc_del"]):
                del structure[model_idx][chain_idx][residue_idx][atom_idx]


    return [{"name": t[0], "num": t[1], "chain": t[2]} for t in new_values]


def save_files(structure: gemmi.Structure, input_file: Path, conformation_type: str, config: Config) -> None:
    """
    Save new structure with no sugar altlocs to file

    :param structure: Structure to be saved
    :param input_file: Path to the original file
    :param conformation_type: Type of conformation A or B
    """
    #FIXME: Options don't work for atom and hetatm lines
    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    new_path = config.modified_mmcif_files_dir / f"{conformation_type}_{input_file.name}"
    structure.make_mmcif_document().write_file(str(new_path), options)


# TODO: Add docs
def separate_alternative_conformations(input_file: Path, config: Config) -> AltlocKind:
    with open(config.run_data_dir / "sugar_names.json") as f:
        sugar_names = set(json.load(f)) # Set for optimalization

    global files_support_altloc
    global files_unsupport_altloc
    global files_single_conform_only

    structure_a = gemmi.read_structure(str(input_file))

    # Lists of alternative conformations
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

                    for atom_idx, atom in enumerate(residue):
                        if atom.altloc != "\0":
                            if atom.altloc == "A":
                                atom_altloc_a.append(atom_idx)
                            elif atom.altloc == "B":
                                atom_altloc_b.append(atom_idx)
                            else:
                                raise AltlocError(input_file.name, atom.altloc)

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
                        altloc_a.append(res_a)
                        res_b = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_b}
                        altloc_b.append(res_b)
                    elif atom_altloc_a or atom_altloc_b:
                        altloc_case = AltlocCase.DOUBLE_RES
                        res = {**common_values, "altloc_case": altloc_case}
                        list_to_append_to = altloc_a if atom_altloc_a else altloc_b
                        list_to_append_to.append(res)


    # if models_count > 1:
        # print(f"More than one model in: {input_file.name}") #NOTE: Learn if normal

    if not altloc_a and not altloc_b:
        return AltlocKind.NO_ALTLOC

    single_altloc_kind = bool(altloc_a) != bool(altloc_b)

    if altloc_a:
        # File with only A conformers
        delete_alternative_conformations(structure_a, altloc_a, altloc_b)
        save_files(structure_a, input_file, "A", config)

    if altloc_b:
        # File with only B conformers
        structure_b = gemmi.read_structure(str(input_file))
        delete_alternative_conformations(structure_b, altloc_b, altloc_a)
        save_files(structure_b, input_file, "B", config)

    return AltlocKind.NORMAL_ALTLOC if not single_altloc_kind else AltlocKind.SINGLE_KIND_ALTLOC     


# TODO: Change to main
def create_separate_mmcifs(config: Config) -> None:
    config.modified_mmcif_files_dir.mkdir(exist_ok=True, parents=True)

    with open(config.categorization_dir / "ligands.json", "r") as f:
        only_ligands: Dict = json.load(f)

    unsupported_altloc = 0
    supported_altloc = 0
    one_altloc_kind = 0

    ids = [id.lower() for id in only_ligands.keys()]
    for file in sorted(config.mmcif_files_dir.glob("*.cif")):
        if file.stem in ids:
            try:
                altloc_kind = separate_alternative_conformations(file, config)
                if altloc_kind == AltlocKind.NO_ALTLOC:
                    copy2(file, config.modified_mmcif_files_dir / f"0_{file.name}")
                elif altloc_kind == AltlocKind.NORMAL_ALTLOC:
                    supported_altloc += 1
                elif altloc_kind == AltlocKind.SINGLE_KIND_ALTLOC:
                    supported_altloc += 1
                    one_altloc_kind += 1
                
            except AltlocError as e:
                unsupported_altloc += 1
                print(f"Exception caught: {e}")

    logger.info(f"Number of files with supported altlocs: {supported_altloc}")
    logger.info(f"Number of files with unsupported altlocs: {unsupported_altloc}")
    logger.info(f"Number of files with just one altloc kind: {one_altloc_kind}")
    
if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)
    
    create_separate_mmcifs(config)
