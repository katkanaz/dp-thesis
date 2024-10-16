import csv
import json

from bs4 import BeautifulSoup, NavigableString

from config import Config


def extract_rscc_and_resolution(config: Config) -> None:
    """
    Extract overall resolution of structures and RSCC values for each of their residues (if said value exists)

    :param config: Config object
    """

    with open(config.categorization_results / "all_residues.json", "r") as f:
        all_residues = json.load(f)
    with open(config.categorization_results / "ligands.json", "r") as f:
        ligands = json.load(f)
    with open(config.categorization_results / "glycosylated.json", "r") as f:
        glycosylated = json.load(f)
    with open(config.categorization_results / "close_contacts.json", "r") as f:
        close_contacts = json.load(f)

    with open(config.validation_results / "all_rscc_and_resolution.csv", "w", newline="") as f:
        all_rscc = csv.writer(f)

        no_resolution = set()
        no_residue_info = set()
        no_rscc = set()

        all_rscc.writerow(["pdb", "resolution", "name", "num", "chain", "rscc", "type"])
        for structure, residues in all_residues.items():
            file = f"{structure.lower()}.xml"
            with open(config.validation_files / file, "r") as file_xml:
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
                #TODO: refactor ifs
                if structure in ligands:
                    if residue in ligands[structure]:
                        res_type = "ligand"
                if structure in glycosylated:
                    if residue in glycosylated[structure]:
                        res_type = "glycosylated"
                if structure in close_contacts:
                    if residue in close_contacts[structure]:
                        res_type = "close"
                #FIXME: Add assert
                row = [str(structure), str(resolution), str(residue["name"]), residue["num"], residue["chain"], str(rscc), res_type]
                all_rscc.writerow(row)


    with open(config.validation_results / "pdb_no_resolution.json", "w") as f:
        json.dump(list(no_resolution), f, indent=4)

    with open(config.validation_results / "no_residue_info.json", "w") as f:
        json.dump(list(no_residue_info), f, indent=4)

    with open(config.validation_results / "no_rscc.json", "w") as f:
        json.dump(list(no_rscc), f, indent=4)


if __name__ == "__main__":
    config = Config.load("config.json")
    config.validation_results.mkdir(exist_ok=True, parents=True)

    extract_rscc_and_resolution(config)
