"""
Script Name: remove_o6.py
Description: Get IDs of structures with available RSCC values
             and remove O6 if one of specific sugars is present.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from csv import DictReader
import json
from logger import setup_logger

from configuration import Config
from utils.hide_altloc import get_possible_altloc_file_names


def get_pdb_ids_with_rscc(config: Config) -> None:
    """
    Get the PDB IDs of structures whose residues have RSCC values

    :param config: Config object
    """

    with open(config.validation_dir / "all_rscc_and_resolution.csv", "r", encoding="utf8") as f:
        rscc = DictReader(f) # FIXME: Use pandas
        pdb_ids = set()
        for row in rscc:
            pdb_ids.add(row["pdb"])
    with open(config.validation_dir / "pdbs_with_rscc_and_resolution.json", "w", encoding="utf8") as f:
        json.dump(list(pdb_ids), f, indent=4)


def remove_o6(config: Config) -> None:
    """
    Remove O6 atom of NAG, GAL, MAN, GLC and BGC from the structures

    :param config: Config object
    """

    with open(config.validation_dir / "pdbs_with_rscc_and_resolution.json", "r", encoding="utf8") as f:
        pdb_ids_of_interest = json.load(f)
    for pdb in pdb_ids_of_interest:
        for file_name in get_possible_altloc_file_names(pdb.lower()):
            try:
                with (config.modified_mmcif_files_dir / f"{file_name}.cif").open() as f:
                    file = f.readlines()
                with (config.no_o6_mmcif_dir / f"{file_name}.cif").open("w") as f:
                    for line in file:
                        if (line.startswith("HETATM") and
                            ("MAN" in line or "NAG" in line or "GAL" in line or "GLC" in line or "BGC" in line) and
                            "O6" in line):
                            continue
                        f.write(line)
                if file_name.startswith("0_"):
                    break
            except:
                pass



def get_ids_and_remove_o6(config: Config) -> None:
    # Tmp # FIXME:
    (config.no_o6_mmcif_dir).mkdir(exist_ok=True, parents=True)

    get_pdb_ids_with_rscc(config)
    remove_o6(config)


if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    get_ids_and_remove_o6(config)
