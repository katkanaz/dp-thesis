"""
Script Name: alternate_conformations.py
Description: Create separate mmCIF files for alternate sugar conformations
Author: Kateřina Nazarčuková
"""


import json
import copy
import gemmi
from gemmi.cif import Block  # type: ignore
from pathlib import Path
from typing import List

from logger import logger, setup_logger
from configuration import Config

def load_mmcif(config: Config) -> List[Path]:
    mmcifs = []
    for file in sorted(Path("").glob("*.cif")):
        mmcifs.append(file)
    
    return mmcifs

def delete_alternate_conformations() -> None:
    pass

def separate_alternate_conformations(input_file: Path) -> None:
    with open("../tmp/alter_conform/sugar_names.json") as f: 
        sugar_names = set(json.load(f)) # Set for optimalization

    structure_a = gemmi.read_structure(str(input_file)) # TODO: Load mmcif file from data directory

    altloc_a: List[Dict] = []
    altloc_b: List[Dict] = []

    models_count = 0
    for model_idx, model in enumerate(structure_a):
        models_count += 1
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                is_altloc = False # TODO: use to log or delete
                if residue.name in sugar_names:
                    atom_altloc_a = []
                    atom_altloc_b = []

                    # NOTE: Can one be sure, one atom won't have a altloc missing
                    # if residue[0].altloc == "\0":
                    #     continue

                    # print(residue.name)
                    for atom_idx, atom in enumerate(residue):
                        # print(atom.name, atom.altloc)
                        if atom.altloc != "\0":
                            is_altloc = True
                            if atom.altloc == "A":
                                atom_altloc_a.append(atom_idx)
                            if atom.altloc == "B":
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
                            print("Not the same number of atoms in each conformation")
                        altloc_case = AltlocCase.SINGLE_RES
                        res_a = {**common_values, "altloc_case": altloc_case, "atom_altloc": atom_altloc_a}
                        altloc_a.append(res_a)
                        res_b = {**common_values, "altloc_case": altloc_case, "atom_altloc": atom_altloc_b}
                        altloc_b.append(res_b)
                    elif atom_altloc_a or atom_altloc_b:
                        altloc_case = AltlocCase.DOUBLE_RES
                        res = {**common_values, "altloc_case": altloc_case}
                        list_to_append_to = altloc_a if atom_altloc_a else altloc_b
                        list_to_append_to.append(res)
    # TODO: Extract to function

    # File with only B conformers
    structure_b = gemmi.read_structure(str(input_file))
    for residue in reversed(altloc_a):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure_b[model_idx][chain_idx][residue_idx]
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc"]):
                del structure_b[model_idx][chain_idx][residue_idx][atom_idx]

    # TODO: Save to file
    new_path = input_file.parent / f"B_{input_file.name}"
    structure_b.make_mmcif_document().write_file(str(new_path))

    # File with only A conformers
    for residue in reversed(altloc_b):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure_a[model_idx][chain_idx][residue_idx]
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc"]):
                del structure_a[model_idx][chain_idx][residue_idx][atom_idx]

    # TODO: Save to file
    new_path_a = input_file.parent / f"A_{input_file.name}"
    structure_a.make_mmcif_document().write_file(str(new_path_a))
                    # print(f"{residue.name} {residue.seqid.num}")
                    # if residue.name == "FUC":
                    #     pass
                        # del residue
                        # del chain[i]
                    # for atom in residue:
                    #     if atom.altloc == "\0":
                    #         # print(f"{residue.name} {residue.seqid.num} {atom.altloc}")
                    #         to_remove_a.add(atom)
                    #         to_remove_b.add(atom)
                    #     if atom.altloc == "A":
                    #         to_remove_a.add(atom)
                    #     if atom.altloc == "B":
                    #         to_remove_b.add(atom)
                    # print(residue.name)
                    
                # if residue.het_flag != "H":
                #     continue
                # if not residue.subchain:
                #     continue

                # res_alter_conforms = {atom.altloc for atom in residue if atom.altloc}
                #
                # if len(res_alter_conforms) > 1:
                #     res_id = f"{residue.name} {residue.seqid.num}"
                #
            # chain.residues = [res for res in chain if res.name != "GAL"]

    # structure_a.make_mmcif_document().write_file('../tmp/alter_conform/new_4d6d.cif')
    # del residue while looping through conformers set
    # will delete it from structure - try duplicate of will have to load twice
    # deep copy python?
    # print(to_remove_a, to_remove_b)
    
    
if __name__ == "__main__":
    # config = Config.load("config.json", None, False)
    #
    # setup_logger(config.log_path)
    
    files = [Path("../tmp/alter_conform/4d6d.cif"), Path("../tmp/alter_conform/7b7c.cif"), Path("../tmp/alter_conform/7c38.cif")]
    # files = [Path("../tmp/alter_conform/new_4d6d.cif")]
    for file in files:
        separate_alternate_conformations(file)
        # print(f"{file.name} done")
