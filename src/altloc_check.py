"""
Script Name: altloc_check.py
Description: Check if alternative conformations of sugars are present
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
import gemmi
from pathlib import Path


def detect_altloc(input_file: Path) -> None:
    with open("../tmp/alter_conform/sugar_names.json") as f: 
        sugar_names = set(json.load(f)) # Set for optimalization

    structure = gemmi.read_structure(str(input_file))

    is_altloc = False
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.name in sugar_names:
                    for atom in residue:
                        if atom.altloc != "\0":
                            is_altloc = True

    if is_altloc:
        print(f"{input_file.name} has alternative conformations")


def detect_altloc_dir(input_file: Path) -> None:
    for file in sorted(input_file.glob("*.cif")):
        detect_altloc(file)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--input_file", help="Input file for altloc detection", type=Path)

    args = parser.parse_args()

    if args.input_file.is_dir():
        detect_altloc_dir(args.input_file)
    else:
        detect_altloc(args.input_file)

