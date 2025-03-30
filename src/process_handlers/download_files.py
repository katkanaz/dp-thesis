"""
Script Name: download_files.py
Description: Acquire IDs of PDB structures with sugars and download said structures and their validation files.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
from os import listdir
from pathlib import Path
from time import sleep
from typing import List, Set

import gemmi
import requests
from logger import logger, setup_logger

from configuration import Config


def get_pdb_ids_from_pq(result_file: Path, config: Config) -> None:
    """
    Get PDB IDs of structures from PQ results

    :param result_file: Path to file for writing results
    :param config: Config object
    """

    structures = set()
    for i in config.sugar_binding_patterns_dir.iterdir():
        structures.add(str(i.name).split("_")[0])
    with open(result_file, "w") as f:
        json.dump(list(structures), f, indent=4)


def get_components_file(config: Config) -> None:
    """
    Download components.cif.gz from CCD

    :param config: Config object
    """

    logger.info("Downloading components file")

    response = requests.get(f"https://files.wwpdb.org/pub/pdb/data/monomers/components.cif.gz")

    with open((config.components_dir / "components.cif.gz"), "wb") as f:
        f.write(response.content)


def get_sugars_from_ccd(config: Config) -> List[str]:
    """Get a list of all sugar abbreviations that appear in PDB database

    :return list: List of sugar abbreviations
    """

    doc = gemmi.cif.read(str(config.components_dir / "components.cif.gz"))
    sugar_names = set()
    for block in doc:
        comp_type = block.get_mmcif_category("_chem_comp.")["type"][0]
        if "saccharide" in comp_type.lower():
            sugar_names.add(block.name)

    with (config.run_data_dir / "sugar_names.json").open("w") as f:
        json.dump(list(sugar_names), f, indent=4)

    return list(sugar_names)


def get_pdb_ids_with_sugars(config: Config, sugar_names: List[str]) -> Set[str]:
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

    with (config.run_data_dir / "pdb_ids_ccd.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)

    sorted_counts = dict(sorted(counts_structures_with_sugar.items(), key=lambda x: x[1], reverse=True))
    with (config.user_cfg.results_dir / "counts_structures_with_sugar.json").open("w") as f:
        json.dump(sorted_counts, f, indent=4)

    with (config.user_cfg.results_dir / "sugars_not_present_in_any_structure.json").open("w") as f:
        json.dump(sugars_not_present_in_any_structure, f, indent=4)

    return pdb_ids


def download_structures_and_validation_files(config: Config, pdb_ids: Set[str]) -> None: # FIXME: Rewrite function to deal with timeout
    """
    Download mmCIF files of structures with sugars and their xml validation files

    :param pdb_ids: PDB IDs of structures to download 
    """

    logger.info("Downloading files")

    failed_to_download = []
    timeout = 2
    n = 0
    for i, pdb in enumerate(pdb_ids):
        try:
            # print(f"Downloading {pdb}")
            response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif")
            open((config.mmcif_files_dir / f"{pdb}.cif"), "wb").write(response.content) 

            validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml")
            open((config.validation_files_dir / f"{pdb}.xml"), "wb").write(validation_data.content)
        except Exception as e:
            logger.info(f"An Error occured: {e}")
            failed_to_download.append(pdb)
            continue

        n += 1
        if n == 20:
            n = 0
            logger.info(f"Pausing for {timeout} seconds. Iteration {i+1}")
            sleep(timeout)

    logger.info("Finished all iterations - first loop.")
    logger.info(failed_to_download)

    # To download files that raised an error in the first loop
    timeout = 2
    n = 0
    for i, pdb in enumerate(failed_to_download):
        logger.info(f"Downloading {pdb}")
        response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif")
        open((config.mmcif_files_dir / f"{pdb}.cif"), "wb").write(response.content) 

        validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml")
        open((config.validation_files_dir / f"{pdb}.xml"), "wb").write(validation_data.content)

        n += 1
        if n == 20:
            n = 0
            logger.info(f"Pausing for {timeout} seconds. Iteration {i+1}")
            sleep(timeout)

    logger.info("Finished all iterations - second loop.")


def get_ids_missing_files(json_file: Path, validation_files: Path) -> List[str]:
    # TODO: Add docs

    missing_files = []
    # Load json with needed structures
    with open(json_file, "r", encoding="utf8") as f:
        all_structures: list[str] = json.load(f)
    # Get a list of downloaded files
    file_names: list[str] = [f.split(".")[0] for f in listdir(validation_files)]
    # Intersect to get a list a files needed to download
    missing_files = [f for f in all_structures if f not in file_names]
    logger.info(missing_files)
    logger.info(len(missing_files))
    return missing_files


def download_missing_files(config: Config, missing_files: List[str]) -> None:
    # TODO: Add docs

    timeout = 2
    n = 0
    while len(missing_files) != 0: 
        for i, pdb in enumerate(missing_files):
            try:
                response = requests.get(f"https://files.rcsb.org/download/{pdb}.cif", timeout=10)
                open((config.mmcif_files_dir / f"{pdb}.cif"), "wb").write(response.content) 

                validation_data = requests.get(f"https://www.ebi.ac.uk/pdbe/entry-files/download/{pdb}_validation.xml", timeout=10)
                open((config.validation_files_dir / f"{pdb}.xml"), "wb").write(validation_data.content)
                missing_files.pop(i)
            except Exception as e:
                logger.info(f"An Error occured: {e}")
                continue

            n += 1
            if n == 50:
                n = 0
                logger.info(f"Pausing for {timeout} seconds. Iteration {i+1}")
                sleep(timeout)


def check_downloaded_files(json_file: Path, validation_files: Path, mmcif_files: Path) -> bool:
    """
    Check if all required structure files were downloaded or not

    :param json_file: IDs of files that should have been downloaded
    :param validation_files: Path to validation files
    :param mmcif_files: Path to mmCIF structure files
    :return: True if all required files were downloaded; False otherwise 
    """

    found_error = False
    with open(json_file, "r") as f:
        all_structures: set[str] = set(json.load(f))
    validation_names: set[str] = set([f.split(".")[0] for f in listdir(validation_files)])
    mmcif_names: set[str] = set([f.split(".")[0] for f in listdir(mmcif_files)])
    if all_structures != validation_names:
        logger.info("Error in validation files")
        logger.info(f"Missing validation files {all_structures - validation_names} {len(all_structures - validation_names)}")
        found_error = True
    if all_structures != mmcif_names:
        logger.info("Error in mmcif files")
        logger.info(f"Missing mmcif files {all_structures - mmcif_names} {len(all_structures - mmcif_names)}")
        found_error = True
    return found_error


def download_files(config: Config, test_mode: bool) -> None:
    # Tmp # FIXME:
    config.run_data_dir.mkdir(exist_ok=True, parents=True)
    config.user_cfg.results_dir.mkdir(exist_ok=True, parents=True)
    config.mmcif_files_dir.mkdir(exist_ok=True, parents=True)
    config.validation_files_dir.mkdir(exist_ok=True, parents=True)
    config.components_dir.mkdir(exist_ok=True, parents=True)

    get_components_file(config)
    sugar_names = get_sugars_from_ccd(config)

    if not test_mode: 
        pdb_ids_pq_file = config.run_data_dir / "pdb_ids_pq.json"
        pdb_ids_ccd = get_pdb_ids_with_sugars(config, sugar_names)
        get_pdb_ids_from_pq(pdb_ids_pq_file, config)

        with (pdb_ids_pq_file).open() as f:
            pdb_ids_pq = json.load(f)
        pdb_ids = set(pdb_ids_ccd).intersection(set(pdb_ids_pq))
    else:
        pdb_ids = set(config.user_cfg.pdb_ids_list)

    with (config.run_data_dir / "pdb_ids_intersection_pq_ccd.json").open("w") as f:
        json.dump(list(pdb_ids), f, indent=4)

    download_structures_and_validation_files(config, pdb_ids)
    check_downloaded_files(config.run_data_dir / "pdb_ids_intersection_pq_ccd.json", config.validation_files_dir, config.mmcif_files_dir)
    missing_files = get_ids_missing_files(config.run_data_dir / "pdb_ids_intersection_pq_ccd.json", config.validation_files_dir)
    download_missing_files(config, missing_files)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-t", "--test_mode", action="store_true", help="Weather to run the whole process in a test mode")

    args = parser.parse_args()

    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    download_files(config, args.test_mode)
