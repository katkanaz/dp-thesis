"""
Script Name: perform_alignment.py
Description: Filter and modify surroundings from PatternQuery and calculate RMSD values by aligning all against all using PyMOL.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import csv
import itertools
import json
import math
import os
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
from tqdm import tqdm
from logger import logger, setup_logger

from configuration import Config

from pymol import cmd, sys


def select_sugar(filename: str) -> Tuple[str, str]:
    """
    Select the desired sugar.

    :param filename: Name of the file to extract the sugar name from
    :return: Name of the sugar and name of the PyMOL selection
    """

    try:
        _, _, res, num, chain = filename.split("_")
    except ValueError:
        _, _, res, num, chain, _ = filename.split("_")

    if len(chain) > 1:
        chain = chain[0]

    sugar = f"/{filename}//{chain}/{res}`{num}"
    selection_name = "sugar"
    cmd.select(selection_name, sugar)

    return sugar, selection_name


def get_sugar_ring_center(sugar: str) -> List[float]:
    """
    Locate the center of the sugar ring.

    :param sugar: Sugar which center needs to be found
    :return: The center coordinates
    """

    return cmd.centerofmass(sugar)


def measure_distances(residues: List[Tuple[str, str]], sugar_center: List[float], filename: str) -> List[Tuple[Tuple[str, str], float]]:
    """
    Measure the distane from all the residues to the sugar center.

    :param residues: The amino acids of the surrounding
    :param sugar_center: Coordinates of the sugar center
    :param filename: Name of the surrounding file which serves as name of the PyMOL object
    :return: Distances of all the residues from the sugar center
    """

    distances: List[Tuple[Tuple[str, str], float]] = []

    cmd.pseudoatom(object="tmp", pos=sugar_center)
    for resi, resn in residues:
        atoms = cmd.get_model(f"resi {resi}").atom
        min_distance = math.inf
        
        for atom in atoms:
            distance = cmd.get_distance(f"{filename} and index {atom.index}", "tmp") # In Angstroms [Å]
            if distance < min_distance:
                min_distance = distance

        distances.append(((resn, resi), min_distance))

    logger.debug(distances)

    cmd.delete("tmp")
    return distances


def sort_distances(distances: List[Tuple[Tuple[str, str], float]], max_res: int) -> List[Tuple[Tuple[str, str], float]]:
    """
    Sort the residue distances in ascending order and keep information of the residues that are over <max_res>.

    :param distances: The distances of the residues from the sugar
    :param max_res: Allowed maximum of residues
    :return: Residues to delete
    """

    sorted_distances = sorted(distances, key=lambda item: item[1])
    return sorted_distances[max_res:]


def remove_residues(residues_to_remove: List[Tuple[Tuple[str, str], float]]) -> None:
    """
    Remove residues from the surrounding.

    :param residues_to_remove: Residues to be deleted
    """

    for (_, resi), _ in residues_to_remove:
        cmd.remove(f"resi {resi}")


def replace_deuterium(file_list: List[Tuple[Path, int]]) -> None:
    """
    Replace deuterium (D) with hydrogen (H)

    :param file_list: Files that need deuterium replacement
    """

    for file in [f[0] for f in file_list]:
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


def refine_binding_sites(sugar: str, min_residues: int, max_residues: int, config: Config, file_list: Union[List[Tuple[Path, int]], None] = None) -> Tuple[Path, List[Tuple[Path, int]]]:
    """
    Filter the surroundings obtained by PQ to contain only the target sugar and at least <min_residues> AA
    and give the filtered structures unique ID, which will be used as an index for creating the
    rmsd matrix.

    :param sugar: The sugar for which the representative surroundings are being defined
    :param min_residues: Minimum of amino acids in the surrounding
    :param max_residues: Maximum of amino acids in the surrounding - necessary for struture motif search later in the process
    :param config: Config object
    :file_list: Surroundings that contain deuterium (D); defaults to None
    :return: Path to refined binding sites folder
    """

    logger.info("Refining sugar surroundings")

    raw_binding_sites = config.raw_binding_sites_dir

    filtered_binding_sites = config.filtered_binding_sites_dir
    filtered_binding_sites.mkdir(exist_ok=True, parents=True)


    less_than_min_aa = []
    more_than_max_aa = []

    deuterium_present = []

    i = 0
    if file_list is not None:
        with open(config.clusters_dir / f"{sugar}_structures_keys.json", "r") as f:
            structures_keys = json.load(f)
    else:
        structures_keys = {} # To map index with structure

    file_source = raw_binding_sites.iterdir() if file_list is None else [file[0] for file in file_list]
    for path_to_file in file_source:


        # FIXME: Delete, to skip mannose surrounding with only one atom
        if str(path_to_file.name) == "0_7zll_MAN_1505_A.pdb" or str(path_to_file.name) == "0_7zll_MAN_1504_A.pdb":
            logger.info(f"Skipping surrounding: {path_to_file.stem}")
            continue

        filename = Path(path_to_file).stem
        logger.debug(f"Begin to process {filename}")
        cmd.delete("all")
        cmd.load(path_to_file)
        count = cmd.count_atoms("n. CA and polymer")
        if count < min_residues:
            less_than_min_aa.append(filename)
            logger.debug(f"{filename} less than 5 residues!")
            continue


        sugar_path, sugar_selection_name = select_sugar(filename)

        cmd.select("wanted_residues", f"{sugar_selection_name} or polymer")
        cmd.select("junk_residues", f"not wanted_residues")
        cmd.remove("junk_residues") 
        cmd.delete("junk_residues")

        if count > max_residues:
            more_than_max_aa.append(filename)
            try:
                sugar_center = get_sugar_ring_center(sugar_selection_name)
            except KeyError as e:
                if str(e) == "'D'":
                    deuterium_present.append((path_to_file, i))
                    logger.warning(f"Found deuterium in: {path_to_file.stem}")
                else:
                    raise e
                i += 1
                continue
            residues: List[Tuple[str, str]] = []
            cmd.iterate("n. CA and polymer", "residues.append((resi, resn))",
                        space=locals())
            
            distances = measure_distances(residues, sugar_center, filename)

            residues_to_remove = sort_distances(distances, max_residues)
            remove_residues(residues_to_remove)


        idx = i
        if file_list is not None:
            idx = list(filter(lambda x: x[0] == path_to_file, file_list))[0][1]
            
        cmd.save(f"{filtered_binding_sites}/{idx}_{filename}.pdb")
        structures_keys[idx] = f"{idx}_{filename}.pdb"
        i += 1
        cmd.delete("all")
        logger.debug(f"{filename} succesfully processed!")

    (config.clusters_dir).mkdir(exist_ok=True, parents=True)
    with open(config.clusters_dir / f"{sugar}_structures_keys.json", "w") as f:
        json.dump(structures_keys, f, indent=4)

    logger.info(f"Number of surroundings with less than {min_residues} AA: {len(less_than_min_aa)}")
    logger.info(f"Number of surroundings with more than {max_residues} AA: {len(more_than_max_aa)}")

    return filtered_binding_sites, deuterium_present


def all_against_all_alignment(sugar: str, structures_folder: Path, perform_align: bool, save_path: Path, config: Config) -> None:
    """
    Calculates all against all RMSD (using PyMol rms_cur command) of all structures firstly aligned
    by their sugar, then aligned by the aminoacids (to find the alignment object - pairs of AA),
    but without actually moving, so the rms_cur is eventually calculated from their position as is
    towards the sugar. Results are saved in a form of distance matrix (.npy) and also as .csv file.

    :param sugar: The sugar for which representative surroundings are being defined
    :param structures_folder: Path to refined binding sites
    :param perform_align: If PyMOL align command was used 
    :param save_path: Path to store .cif files fetched by PyMOL
    :param config: Config object
    """

    logger.info("Performing alignment")

    super_results_path = config.clusters_dir / "super"
    super_results_path.mkdir(parents=True, exist_ok=True)

    n = len(os.listdir(structures_folder))
    super_rmsd_values = np.zeros((n, n))
    align_rmsd_values = np.zeros((n, n))

    something_wrong = []

    align_writer = None
    align_results_path = None
    align_file = None
    if perform_align:
        align_results_path = config.clusters_dir / "align"
        align_results_path.mkdir(parents=True, exist_ok=True)

        align_file = open(align_results_path / f"{sugar}_all_pairs_rmsd_align.csv", "w", newline="")
        align_writer = csv.writer(align_file)
        align_writer.writerow(["structure1", "structure2", "rmsd"])

    with open(super_results_path / f"{sugar}_all_pairs_rmsd_super.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["structure1", "structure2", "rmsd"])
        all_structures = os.listdir(structures_folder)
        with tqdm(total=math.comb(len(all_structures), 2), desc="Aligning files") as pbar: 
            for (structure1, structure2) in itertools.combinations(all_structures, 2):
                pbar.update(1)
                try:
                    cmd.delete("all")
                    cmd.load(f"{structures_folder}/{structure1}")
                    cmd.load(f"{structures_folder}/{structure2}")

                    cmd.fetch(sugar, path=str(save_path))

                    filename1 = Path(structure1).stem
                    filename2 = Path(structure2).stem

                    try:
                        id1, _, _, res1, num1, chain1 = filename1.split("_")
                    except ValueError:
                        id1, _, _, res1, num1, chain1, _ = filename1.split("_")
                    try:
                        id2, _, _, res2, num2, chain2 = filename2.split("_")
                    except ValueError:
                        id2, _, _, res2, num2, chain2, _ = filename2.split("_")
                    # Some structures have chains named eg. AaA but when loaded to PyMol
                    # the the chain is reffered to just as A.
                    if len(chain1) > 1:
                        chain1 = chain1[0]
                    if len(chain2) > 1:
                        chain2 = chain2[0] 

                    sugar1 = f"/{filename1}//{chain1}/{res1}`{num1}"
                    sugar2 = f"/{filename2}//{chain2}/{res2}`{num2}"

                    cmd.select("original_sugar1", sugar1)
                    cmd.select("original_sugar2", sugar2)
                    cmd.select("polymer1", f"polymer and not {filename2}")
                    cmd.select("polymer2", f"polymer and not {filename1}")

                    cmd.align("original_sugar1", sugar)
                    cmd.align("original_sugar2", sugar)

                    cmd.super("polymer1", "polymer2", transform=0, cycles=0, object="sup") 
                    rms = float(cmd.rms_cur("polymer1 & sup", "polymer2 & sup", matchmaker=-1))

                    writer.writerow([filename1, filename2, rms])
                    super_rmsd_values[int(id1), int(id2)] = rms 
                    super_rmsd_values[int(id2), int(id1)] = rms

                    if perform_align:
                        assert align_writer is not None, "If perform_align is true, align_writer has to exist"
                        cmd.align("polymer1", "polymer2", transform=0, cycles=0, object="aln")
                        rms = float(cmd.rms_cur("polymer1 & aln", "polymer2 & aln", matchmaker=-1))
                        align_writer.writerow([filename1, filename2, rms])
                        align_rmsd_values[int(id1), int(id2)] = rms 
                        align_rmsd_values[int(id2), int(id1)] = rms

                    cmd.delete("all") 
                except Exception as e:
                    # Save pairs with which something went wrong
                    something_wrong.append((structure1, structure2))
                    logger.error(f"Something went wrong: {e}")

    if align_file is not None and align_results_path is not None:
        align_file.close()
        np.save(align_results_path / f"{sugar}_all_pairs_rmsd_align.npy", align_rmsd_values)

    np.save(super_results_path / f"{sugar}_all_pairs_rmsd_super.npy", super_rmsd_values)
    with open((config.clusters_dir / "something_wrong.json"), "w") as f:
        json.dump(something_wrong, f, indent=4)

    if something_wrong:
        raise Exception("Something went wrong not empty")


def perform_alignment(sugar: str, perform_align: bool, config: Config) -> None:
    # Fixed values based on literature and structure motif search limit
    # TODO: Extract as arguments with default
    min_residues = 5
    max_residues = 10

    fixed_folder, deuterium_present = refine_binding_sites(sugar, min_residues, max_residues, config)
    if deuterium_present:
        replace_deuterium(deuterium_present)
        logger.info("Refining binding sites with replaced deuterium")
        refine_binding_sites(sugar, min_residues, max_residues, config, deuterium_present)
    sys.stdout.flush()

    save_path = config.sugars_dir
    save_path.mkdir(exist_ok=True, parents=True)
    all_against_all_alignment(sugar, fixed_folder, perform_align, save_path, config)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    try:
        perform_alignment(args.sugar, args.perform_align, config)
    except Exception as e:
        logger.error(f"Exception caught: {e}")
        raise e

