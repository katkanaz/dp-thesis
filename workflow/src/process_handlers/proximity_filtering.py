"""
Script Name: 
Description: 
Author: Kateřina Nazarčuková
"""
# TODO: fix 


from argparse import ArgumentParser
import json
import math
from logger import logger, setup_logger
from pathlib import Path
from tqdm import tqdm
from typing import List, Tuple, Union

from configuration import Config

from pymol import cmd
from .perform_alignment import select_sugar


def get_sugar_ring_center(sugar: str) -> List[float]:
    """
    Locate the center of the sugar ring.

    :param sugar: Sugar which center needs to be found
    :return: The center coordinates
    """

    return cmd.centerofmass(sugar)


def measure_distances(residues: List[Tuple[str, str, str]], sugar_center: List[float], filename: str) -> List[Tuple[Tuple[str, str, str], float]]:
    """
    Measure the distane from all the residues to the sugar center.

    :param residues: The amino acids of the surrounding
    :param sugar_center: Coordinates of the sugar center
    :param filename: Name of the surrounding file which serves as name of the PyMOL object
    :return: Distances of all the residues from the sugar center
    """

    distances: List[Tuple[Tuple[str, str, str], float]] = []

    cmd.pseudoatom(object="tmp", pos=sugar_center)
    for resi, resn, chain in residues:
        atoms = cmd.get_model(f"resi {resi}").atom
        min_distance = math.inf
        
        for atom in atoms:
            distance = cmd.get_distance(f"{filename} and index {atom.index}", "tmp") # In Angstroms [Å]
            if distance < min_distance:
                min_distance = distance

        distances.append(((resi, resn, chain), min_distance))


    cmd.delete("tmp")
    return distances


def sort_distances(distances: List[Tuple[Tuple[str, str, str], float]], max_res: int) -> List[Tuple[Tuple[str, str, str], float]]:
    """
    Sort the residue distances in ascending order and keep information of the residues that are over <max_res>.

    :param distances: The distances of the residues from the sugar
    :param max_res: Allowed maximum of residues
    :return: Residues to delete
    """
    # If 2 residues same distance the one with the lower number and chain with the earlier alphabetical ID goes first
    sorted_distances = sorted(distances, key=lambda item: (item[1], int(item[0][0]), item[0][2]))
    return sorted_distances[max_res:]


def remove_residues(residues_to_remove: List[Tuple[Tuple[str, str, str], float]]) -> None:
    """
    Remove residues from the surrounding.

    :param residues_to_remove: Residues to be deleted
    """

    for (resi, resn, chain), _ in residues_to_remove:
        selection = f"chain {chain} and resi {resi} and resn {resn}"
        cmd.remove(selection)


def replace_deuterium(file_list: List[Tuple[Path, int]]) -> None:
    """
    Replace deuterium (D) with hydrogen (H)

    :param file_list: Files that need deuterium replacement
    """

    for file, _ in file_list:
        logger.info(f"Replacing deuterium for file: {file}")
        with open(file, "r") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line[76:78] == " D":
                chars = list(line)
                chars[77] = "H"
                line = "".join(chars)
            new_lines.append(line)
        with open(file, "w") as f:
            f.writelines(new_lines)


def extract_and_process_representatives(sugar: str, number: int, method: str, config: Config, input_representatives: Path, max_residues: int, file_list: Union[List[Tuple[Path, int]], None] = None) -> List[Tuple[Path, int]]:
    """
    Extract files of representatives for structure motif search and perform proximity filtering.

    :param sugar: The sugar for which the representative surroundings are defined 
    :param number: The number of created clusters
    :param method: The clustering method
    :param config: Config object
    :param input_representatives: Folder to extract representatives in
    :param max_residues: Maximum of amino acids in the surrounding - necessary for struture motif search later in the process
    :file_list: Surroundings that contain deuterium (D); defaults to None
    """

    if file_list is None:
        logger.info("Extracting representatives")
    else:
        logger.info("Extracting representatives that used to have deuterium")

    with open(config.clusters_dir / "super" / f"{number}_{method}_cluster_representatives.json") as rep_file:
        representatives: dict = json.load(rep_file)
    with open(config.clusters_dir / f"{sugar}_structures_keys.json") as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)

    more_than_max_aa = []
    deuterium_present: List[Tuple[Path, int]] = []

    file_keys = [file_key for _, file_key in representatives.items()] if file_list is None else [file[1] for file in file_list]
    for file_key in file_keys:
        path_to_surrounding_file = Path(config.filtered_surroundings_dir / structure_keys[str(file_key)])
        surrounding_file_name = path_to_surrounding_file.stem

        cmd.delete("all")
        cmd.load(path_to_surrounding_file)
        count = cmd.count_atoms("n. CA and polymer")
        sugar, sugar_selection_name = select_sugar(surrounding_file_name)
        logger.debug(f"Sugar is {sugar}")

        if count > max_residues:
            more_than_max_aa.append(surrounding_file_name)
            logger.debug(f"{surrounding_file_name} more than 10 residues!")
            try:
                sugar_center = get_sugar_ring_center(sugar_selection_name)
            except KeyError as e:
                if str(e) == "'D'":
                    deuterium_present.append((path_to_surrounding_file, file_key))
                    logger.warning(f"Found deuterium in: {path_to_surrounding_file.stem}")
                else:
                    raise e
                continue
            residues: List[Tuple[str, str, str]] = []
            cmd.iterate("n. CA and polymer", "residues.append((resi, resn, chain))", space=locals())
            logger.debug(f"Residues list: {residues}")
            
            distances = measure_distances(residues, sugar_center, surrounding_file_name)

            residues_to_remove = sort_distances(distances, max_residues)
            remove_residues(residues_to_remove)

        cmd.save(f"{input_representatives}/{surrounding_file_name}.pdb")
        cmd.delete("all")
        logger.debug(f"{surrounding_file_name} succesfully processed!")

    logger.info(f"Number of surroundings with more than {max_residues} AA: {len(more_than_max_aa)}")

    return deuterium_present


def main(sugar: str, number: int, method: str, config: Config, max_residues: int):
    input_folder = config.structure_motif_search_dir / "input_representatives"
    input_folder.mkdir(exist_ok=True, parents=True)

    deuterium_present = extract_and_process_representatives(sugar, number, method, config, input_folder, max_residues)
    if deuterium_present:
        replace_deuterium(deuterium_present)
        logger.info("Refining binding sites with replaced deuterium")
        extract_and_process_representatives(sugar, number, method, config, input_folder, max_residues, deuterium_present)

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-t", "--test_mode", action="store_true",
                        help="Weather to run the whole process in a test mode")
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-c", "--perform_clustering", action="store_true", help="Whether to perform data clustering of filtered surroundings")
    parser.add_argument("-n", "--number", help="Number of clusters", type=int, default=20)
    parser.add_argument("-m", "--method", help="Cluster method", type=str, default="centroid")
    parser.add_argument("--max_residues", help="Maximum number of residues in a surrunding. Required by structure motif search", type=int, default=10)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True, args)

    setup_logger(config.log_path)

    main(args.sugar, args.number, args.method, config, args.max_residues)

