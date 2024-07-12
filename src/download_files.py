import json
from os import listdir
from pathlib import Path

import gemmi
import requests
from time import sleep

from config import Config


def get_pdb_ids_from_pq(result_file: Path) -> None:
    """
    Get PDB IDs of structures from PQ results

    :param result_file: Path to file for writing results
    """

    structures = set()
    for i in config.patterns_folder.iterdir():
        structures.add(str(i.name).split("_")[0])
    with open(result_file, "w") as f:
        json.dump(list(structures), f, indent=4)


def get_components_file() -> None:
    """
    Download components.cif.gz from CCD
    """

    response = requests.get(f"https://files.wwpdb.org/pub/pdb/data/monomers/components.cif.gz")
    with open(str(config.data_folder / "components.cif.gz"), "wb") as f:
        f.write(response.content)


def get_sugars_from_ccd() -> list:
    """Get a list of all sugar abbreviations that appear in PDB database

    :return list: List of sugar abbreviations
    """

    doc = gemmi.cif.read(str(config.data_folder / "components.cif.gz"))
    sugar_names = set()
    for block in doc:
        comp_type = block.get_mmcif_category("_chem_comp.")["type"][0]
        if "saccharide" in comp_type.lower():
            sugar_names.add(block.name)

    with (config.data_folder / "sugar_names.json").open("w") as f:
        json.dump(list(sugar_names), f, indent=4)
    return list(sugar_names)


def get_pdb_ids_with_sugars(sugar_names: list) -> set:
    """Get a set of PDB IDs for all structures containing any of the sugars

    :param list sugar_names: List of sugar abbreviations
    :return set: Set of PDB IDs belonging to structures with the sugars
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

    with (config.data_folder / "pdb_ids_ccd.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)

    sorted_counts = dict(sorted(counts_structures_with_sugar.items(), key=lambda x: x[1], reverse=True))
    with (config.results_folder / "counts_structures_with_sugar.json").open("w") as f:
        json.dump(sorted_counts, f, indent=4)

    with (config.results_folder / "sugars_not_present_in_any_structure.json").open("w") as f:
        json.dump(sugars_not_present_in_any_structure, f, indent=4)

    return pdb_ids


def download_structures_and_validation_files(pdb_ids: set) -> None:#FIXME: Rewrite function to deal with timeout
    """
    Download mmCIF files of structures with sugars and their xml validation files

    :param pdb_ids: PDB IDs of structures to download 
    """

    print("Downloading files")

    failed_to_download = []
    timeout = 2
    n = 0
    for i, pdb in enumerate(pdb_ids):
        try:
            # print(f"Downloading {pdb}")
            response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif")
            open(str(config.mmcif_files / f"{pdb}.cif"), "wb").write(response.content) 

            validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml")
            open(str(config.validation_files / f"{pdb}.xml"), "wb").write(validation_data.content)
        except Exception as e:
            print(f"An Error occured: {e}")
            failed_to_download.append(pdb)
            continue

        n += 1
        if n == 20:
            n = 0
            print(f"Pausing for {timeout} seconds. Iteration {i+1}")
            sleep(timeout)

    print("Finished all iterations - first loop.")
    print(failed_to_download)

    # To download files that raised an error in the first loop
    timeout = 2
    n = 0
    for i, pdb in enumerate(failed_to_download):
        print(f"Downloading {pdb}")
        response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif")
        open(str(config.mmcif_files / f"{pdb}.cif"), "wb").write(response.content) 

        validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml")
        open(str(config.validation_files / f"{pdb}.xml"), "wb").write(validation_data.content)

        n += 1
        if n == 20:
            n = 0
            print(f"Pausing for {timeout} seconds. Iteration {i+1}")
            sleep(timeout)

    print("Finished all iterations - second loop.")


def get_ids_missing_files(json_file: Path, validation_files: Path) -> list:
    #TODO: Add docs
    missing_files = []
    # Load json with needed structures
    with open(json_file, "r") as f:
        all_structures: list[str] = json.load(f)
    # Get a list of downloaded files
    file_names: list[str] = [f.split(".")[0] for f in listdir(validation_files)]
    # Intersect to get a list a files needed to download
    missing_files = [f for f in all_structures if f not in file_names]
    print(missing_files)
    print(len(missing_files))
    return missing_files


def download_missing_files(missing_files: list) -> None:
    #TODO: Add docs
    timeout = 2
    n = 0
    while len(missing_files) != 0: 
        for i, pdb in enumerate(missing_files):
            try:
                response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif", timeout=10)
                open(str(config.mmcif_files / f"{pdb}.cif"), "wb").write(response.content) 

                validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml", timeout=10)
                open(str(config.validation_files / f"{pdb}.xml"), "wb").write(validation_data.content)
                missing_files.pop(i)
            except Exception as e:
                print(f"An Error occured: {e}")
                continue

            n += 1
            if n == 50:
                n = 0
                print(f"Pausing for {timeout} seconds. Iteration {i+1}")
                sleep(timeout)

def check_downloaded_files(json_file: Path, validation_files: Path, mmcif_files: Path) -> bool:
    #TODO: Add docs
    found_error = False
    with open(json_file, "r") as f:
        all_structures: set[str] = set(json.load(f))
    validation_names: set[str] = set([f.split(".")[0] for f in listdir(validation_files)])
    mmcif_names: set[str] = set([f.split(".")[0] for f in listdir(mmcif_files)])
    if all_structures != validation_names:
        print("Error in validation files")
        print(f"Missing validation files {all_structures - validation_names} {len(all_structures - validation_names)}")
        found_error = True
    if all_structures != mmcif_names:
        print("Error in mmcif files")
        print(f"Missing mmcif files {all_structures - mmcif_names} {len(all_structures - mmcif_names)}")
        found_error = True
    return found_error


def main(config: Config):
    pdb_ids_pq_file = config.data_folder / "pdb_ids_pq.json"
    #get_components_file()
    sugar_names = get_sugars_from_ccd()
    pdb_ids_ccd = get_pdb_ids_with_sugars(sugar_names)
    get_pdb_ids_from_pq(pdb_ids_pq_file)

    with (pdb_ids_pq_file).open() as f:
        pdb_ids_pq = json.load(f)
    pdb_ids = set(pdb_ids_ccd).intersection(set(pdb_ids_pq))
    with (config.data_folder / "pdb_ids_intersection_pq_ccd.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)

    download_structures_and_validation_files(pdb_ids)
    check_downloaded_files(config.data_folder / "pdb_ids_intersection_pq_ccd.json", config.validation_files, config.mmcif_files)

    # missing_files = get_ids_missing_files(config.data_folder / "pdb_ids_intersection_pq_ccd.json", config.validation_files)
    # download_missing_files(missing_files)

if __name__ == "__main__":
    config = Config.load("config.json")

    config.data_folder.mkdir(exist_ok=True, parents=True)
    config.results_folder.mkdir(exist_ok=True, parents=True)
    config.mmcif_files.mkdir(exist_ok=True, parents=True)
    config.validation_files.mkdir(exist_ok=True, parents=True)

    main(config)
