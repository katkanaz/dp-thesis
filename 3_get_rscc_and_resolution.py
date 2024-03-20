import csv
import json
from pathlib import Path

from bs4 import BeautifulSoup


RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
DATA_FOLDER = Path("/Volumes/YangYang/diplomka") / "data"

categorized_pdbs_path = RESULTS_FOLDER / "categorization"
validation_files_path = DATA_FOLDER / "validation_files"

results_path = RESULTS_FOLDER / "validation"
results_path.mkdir(exist_ok=True)


def extract_rscc_and_resolution():
    with open(categorized_pdbs_path / "all_residues.json", "r") as f:
        all_residues = json.load(f)
    with open(categorized_pdbs_path / "ligands.json", "r") as f:
        ligands = json.load(f)
    with open(categorized_pdbs_path / "glycosylated.json", "r") as f:
        glycosylated = json.load(f)
    with open(categorized_pdbs_path / "close_contacts.json", "r") as f:
        close_contacts = json.load(f)

    with open(results_path / "all_rscc_and_resolution.csv", "w", newline="") as f:
        all_rscc = csv.writer(f)

        no_resolution = set()
        no_residue_info = set()
        no_rscc = set()

        all_rscc.writerow(["pdb", "resolution", "name", "num", "chain", "rscc", "type"])
        for structure, residues in all_residues.items():
            file = f"{structure.lower()}.xml"
            with open(validation_files_path / file, "r") as file_xml:
                d = file_xml.read()
            data = BeautifulSoup(d, "xml")
            structure_info = data.find("Entry")
            resolution = structure_info.get("PDB-resolution")
            if not resolution:
                no_resolution.add(structure)
                continue
            for residue in residues:
                residue_info = data.find("ModelledSubgroup", attrs={"resnum": residue["num"], "chain": residue["chain"], "resname": residue["name"]})
                if not residue_info:
                    no_residue_info.add(f"{structure}_{residue}")
                    continue

                rscc = residue_info.get("rscc")
                if not rscc:
                    no_rscc.add(f"{structure}_{residue}")
                    continue
                if structure in ligands:
                    if residue in ligands[structure]:
                        res_type = "ligand"
                if structure in glycosylated:
                    if residue in glycosylated[structure]:
                        res_type = "glycosylated"
                if structure in close_contacts:
                    if residue in close_contacts[structure]:
                        res_type = "close"
                row = [str(structure), str(resolution), str(residue["name"]), residue["num"], residue["chain"], str(rscc), res_type]
                all_rscc.writerow(row)


    with open(results_path / "pdb_no_resolution.json", "w") as f:
        json.dump(list(no_resolution), f, indent=4)

    with open(results_path / "no_residue_info.json", "w") as f:
        json.dump(list(no_residue_info), f, indent=4)

    with open(results_path / "no_rscc.json", "w") as f:
        json.dump(list(no_rscc), f, indent=4)


if __name__ == "__main__":
    extract_rscc_and_resolution()