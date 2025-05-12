"""
Script Name: perform_alignment.py
Description: Filter and modify binding sites from PatternQuery and calculate RMSD values by aligning all against all using PyMOL.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import csv
import itertools
import json
import os
from pathlib import Path

import numpy as np
from logger import logger, setup_logger

from configuration import Config

from pymol import cmd


# TODO: Refactor function
# FIXME: Function description
def refine_binding_sites(sugar: str, min_residues: int, max_residues: int, config: Config) -> Path:
    """
    Filter the binding sites obtained by PQ to contain only the target sugar and at least <min_res> AA
    and give the filtered structures unique ID, which will be used as an index for creating the
    rmsd matrix.

    :param sugar: The sugar for which representative binding sites are being defined
    :param min_res: Minimum of amino acids in the binding site
    :param config: Config object
    :return: Path to refined binding sites folder
    """

    raw_binding_sites = config.raw_binding_sites_dir

    filtered_binding_sites = config.filtered_binding_sites_dir
    filtered_binding_sites.mkdir(exist_ok=True, parents=True)

    less_than_n_aa = []
    more_than_max_aa = []
    i = 0
    structures_keys = {} # To map index with structure
    for path_to_file in raw_binding_sites.iterdir():
        filename = Path(path_to_file).stem
        cmd.delete("all")
        cmd.load(path_to_file)
        count = cmd.count_atoms("n. CA and polymer")
        if count < min_residues:
            less_than_n_aa.append(filename)
            continue

        try:
            _, _, res, num, chain = filename.split("_")
        except ValueError:
            _, _, res, num, chain, _ = filename.split("_")
        # Some structures have chains named eg. AaA but when loaded to PyMol
        # the the chain is reffered to just as A.
        if len(chain) > 1:
            chain = chain[0]

        current_sugar = f"/{filename}//{chain}/{res}`{num}"

        cmd.select("wanted_residues", f"{current_sugar} or polymer")
        cmd.select("junk_residues", f"not wanted_residues")
        cmd.remove("junk_residues") 
        cmd.delete("junk_residues")

        cmd.save(f"{filtered_binding_sites}/{i}_{filename}.pdb")
        structures_keys[i] = f"{i}_{filename}.pdb"
        i += 1
        cmd.delete("all")

    (config.clusters_dir).mkdir(exist_ok=True, parents=True)
    with open(config.clusters_dir / f"{sugar}_structures_keys.json", "w") as f:
        json.dump(structures_keys, f, indent=4)

    logger.info(f"Number of surroundings with less than {min_residues} AA: {len(less_than_n_aa)}")

    return filtered_binding_sites


    # Calculates all against all RMSD (using PyMol rms_cur command) of all structures firstly aligned
    # by their sugar, then aligned by the aminoacids (to find the alignment object - pairs of AA),
    # but without actually moving, so the rms_cur is eventually calculated from their position as is
    # towards the sugar. Results are saved in a form of distance matrix (.npy) and also as .csv file.
# TODO: Refactor function
# FIXME: Function description
def all_against_all_alignment(sugar: str, structures_folder: Path, perform_align: bool, save_path: Path, config: Config) -> None:
    """
    [TODO:description]

    :param sugar: The sugar for which representative binding sites are being defined
    :param structures_folder: Path to refined binding sites
    :param method: The PyMOL command used to calculate RMSD
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
        for (structure1, structure2) in itertools.combinations(os.listdir(structures_folder), 2):
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


def perform_alignment(sugar: str, perform_align: bool, config: Config) -> None:
    # Fixed values based on literature and structure motif search limit
    # TODO: Extract as arguments with default
    min_residues = 5
    max_residues = 10

    fixed_folder = refine_binding_sites(sugar, min_residues, max_residues, config)

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

    perform_alignment(args.sugar, args.perform_align, config)
