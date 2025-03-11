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

    structure_a = gemmi.read_structure(str(input_file))
    structure_b = gemmi.read_structure(str(input_file))


    to_remove_a = set()
    to_remove_b = set()

    for model in structure_a:
        for chain in model:
            # chain.residues = [res for res in chain if res.name != "GAL"]
            for i, residue in reversed(list(enumerate(chain))):
                if residue.name in sugar_names:
                    print(f"{residue.name} {residue.seqid.num}")
                    if residue.name == "FUC":
                        pass
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
    for file in files:
        separate_alternate_conformations(file)
        print(f"{file.name} done")
