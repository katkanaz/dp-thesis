"""
Script Name: extract_rscc_and_resolution.py
Description: Extract resolution of structures and RSCC values of their residues if available.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


import csv
import json

from bs4 import BeautifulSoup, NavigableString
from logger import logger, setup_logger

from configuration import Config
from utils.hide_altloc import find_residue_any_altloc, remove_altloc_from_id


def extract_rscc_and_resolution(config: Config) -> None:
    """
    Extract overall resolution of structures and RSCC values for each of their residues (if said value exists).

    :param config: Config object
    """

    # Tmp # FIXME:
    config.validation_dir.mkdir(exist_ok=True, parents=True)

    logger.info("Extracting RSCC and resolution")

    with open(config.categorization_dir / "all_residues.json", "r", encoding="utf8") as f:
        all_residues = json.load(f)
    with open(config.categorization_dir / "modified_ligands.json", "r", encoding="utf8") as f:
        modified_ligands = json.load(f)
    with open(config.categorization_dir / "glycosylated.json", "r", encoding="utf8") as f:
        glycosylated = json.load(f)
    with open(config.categorization_dir / "close_contacts.json", "r", encoding="utf8") as f:
        close_contacts = json.load(f)

    with open(config.validation_dir / "all_rscc_and_resolution.csv", "w", newline="", encoding="utf8") as f:
        all_rscc = csv.writer(f)

        no_resolution = set()
        no_residue_info = set()
        no_rscc = set()

        modified_ids_no_altloc = [remove_altloc_from_id(pdb_id) for pdb_id in modified_ligands]
        all_rscc.writerow(["pdb", "resolution", "name", "num", "chain", "rscc", "type"])
        for structure, residues in all_residues.items():
            file = f"{structure.lower()}.xml.gz" # FIXME: After fixed on pdb end, read binary via gzip.open() and do not save
            with open(config.validation_files_dir / file, "r", encoding="utf8") as file_xml:
                d = file_xml.read()
            data = BeautifulSoup(d, "xml")
            structure_info = data.find("Entry")
            if structure_info is None or isinstance(structure_info, NavigableString):
                continue
            resolution = structure_info.get("PDB-resolution")
            if not resolution:
                no_resolution.add(structure)
                continue
            for residue in residues:
                residue_info = data.find("ModelledSubgroup", attrs={"resnum": residue["num"], "chain": residue["chain"], "resname": residue["name"]})
                if not residue_info:
                    no_residue_info.add(f"{structure}_{residue}")
                    continue

                if residue_info is None or isinstance(residue_info, NavigableString):
                    continue
                rscc = residue_info.get("rscc")
                if not rscc:
                    no_rscc.add(f"{structure}_{residue}")
                    continue

                res_type = None
                # print(structure)
                # print(modified_ids_no_altloc)
                if structure in modified_ids_no_altloc and find_residue_any_altloc(modified_ligands, structure, residue):
                        res_type = "ligand"
                if structure in glycosylated and residue in glycosylated[structure]:
                        res_type = "glycosylated"
                if structure in close_contacts and residue in close_contacts[structure]:
                        res_type = "close"
                # assert res_type is not None, "Residue should be one of the following type: ligand, glycosylated, close contact" 

                # Structure can have unsupported altloc, therefore is not in any category
                if res_type is None:
                    continue # FIXME: Refactor with this issue
                row = [str(structure), str(resolution), str(residue["name"]), residue["num"], residue["chain"], str(rscc), res_type]
                all_rscc.writerow(row)


    with open(config.validation_dir / "pdb_no_resolution.json", "w", encoding="utf8") as f:
        json.dump(list(no_resolution), f, indent=4)

    with open(config.validation_dir / "no_residue_info.json", "w", encoding="utf8") as f:
        json.dump(list(no_residue_info), f, indent=4)

    with open(config.validation_dir / "no_rscc.json", "w", encoding="utf8") as f:
        json.dump(list(no_rscc), f, indent=4)


if __name__ == "__main__":
    config = Config.load("config.json", None, False, None)

    setup_logger(config.log_path)

    extract_rscc_and_resolution(config)
