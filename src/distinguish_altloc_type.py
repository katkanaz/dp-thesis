"""
Script Name: distinguish_altloc_type.py
Description: How many files have altlocs different than A or B or null Byte and what kind
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
import gemmi
from pathlib import Path


def detect_altloc(input_file: Path) -> bool:
    with open("../tmp/alter_conform/sugar_names.json") as f: 
        sugar_names = set(json.load(f)) # Set for optimalization

    structure = gemmi.read_structure(str(input_file))

    different_altloc = False
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.name in sugar_names:
                    for atom in residue:
                        if atom.altloc != "\0" and atom.altloc != "A" and atom.altloc != "B":
                            print(type(atom.altloc), atom.altloc, input_file.name)
                            different_altloc = True
                            
    return different_altloc


def detect_altloc_dir(input_file: Path) -> None:
    count = 0
    for file in sorted(input_file.glob("*.cif")):
        different_altloc = detect_altloc(file)
        if different_altloc:
            count += 1

    print(f"Number of structures with different altloc types: {count}")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--input_file", help="Input file for altloc detection", type=Path)

    args = parser.parse_args()

    if args.input_file.is_dir():
        detect_altloc_dir(args.input_file)
    else:
        detect_altloc(args.input_file)
