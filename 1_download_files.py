import json
from pathlib import Path

import gemmi
import requests


RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
DATA_FOLDER = Path("/Volumes/YangYang/diplomka") / "data"

RESULTS_FOLDER.mkdir(exist_ok=True)


def get_sugars_from_ccd():
    """
    Gets a set of all sugar abbreviations that appear in PDB database.
    """
    doc = gemmi.cif.read(str(DATA_FOLDER / "components.cif.gz"))
    sugars = set()
    for block in doc:
        comp_type = block.get_mmcif_category("_chem_comp.")["type"][0]
        if "saccharide" in comp_type.lower():
            sugars.add(block.name)

    with (DATA_FOLDER / "sugar_names.json").open("w") as f:
        json.dump(list(sugars), f, indent=4)
    
    return list(sugars)


def get_pdb_ids_with_sugars(sugar_names: list):
    """
    Gets a set of all PDB IDs of structures containing any of the sugars.
    """
    pdb_ids = set()
    counts_structures_with_sugar = {} 
    sugars_not_present_in_any_structure = []
    for sugar in sugar_names:
        response = requests.get(f"https://www.ebi.ac.uk/pdbe/api/pdb/compound/in_pdb/{sugar}")
        structures = response.json()
        if not structures:
            sugars_not_present_in_any_structure.append(sugar)
            continue
        pdb_ids.update(structures[sugar])
        counts_structures_with_sugar[sugar] = len(structures[sugar])

    with (DATA_FOLDER / "pdb_ids_CCD.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)
    
    sorted_counts = dict(sorted(counts_structures_with_sugar.items(), key=lambda x: x[1], reverse=True))
    with (RESULTS_FOLDER / "counts_structures_with_sugar.json").open("w") as f:
        json.dump(sorted_counts, f, indent=4)

    with (RESULTS_FOLDER / "sugars_not_present_in_any_structure.json").open("w") as f:
        json.dump(sugars_not_present_in_any_structure, f, indent=4)
    
    return pdb_ids


def download_structures_and_validation_files(pdb_ids: set):
    """
    Downloads mmCIF files of structures containing sugars and their xml validation files.
    """
    (DATA_FOLDER / "mmCIF_files").mkdir()
    (DATA_FOLDER / "validation_files").mkdir()

    for pdb in pdb_ids:
        response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif")
        open(str(DATA_FOLDER / "mmCIF_files" / f"{pdb}.cif"), "wb").write(response.content)

        validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml")
        open(str(DATA_FOLDER / "validation_files" / f"{pdb}.xml"), "wb").write(validation_data.content)


def main():
    sugar_names = get_sugars_from_ccd()
    pdb_ids_ccd = get_pdb_ids_with_sugars(sugar_names)

    with (DATA_FOLDER / "pdb_ids_PQ.json").open() as f:
        pdb_ids_PQ = json.load(f)
    pdb_ids = set(pdb_ids_ccd).intersection(set(pdb_ids_PQ))
    with (DATA_FOLDER / "pdb_ids_intersection_PQ_CCD.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)

    download_structures_and_validation_files(pdb_ids)


if __name__ == "__main__":
    main()
