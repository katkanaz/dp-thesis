from argparse import ArgumentParser
import csv
import itertools
import json
import os
from pathlib import Path

import numpy as np

from config import Config
from pymol_api import Pymol


def refine_binding_sites(sugar: str, min_res: int, config: Config, pm_cmd: Pymol) -> Path:
    """
    Filter the binding sites obtained by PQ to contain only the target sugar and at least <min_res> AA
    and give the filtered structures unique ID, which will be used as an index for creating the
    rmsd matrix.

    :param sugar: The sugar for which representative binding sites are being defined
    :param min_res: Minimum of amino acids in the binding site
    :param config: Config object
    :return: Path to refined binding sites folder
    """
    # Path to the folder containing the PDB structures from PQ
    structures_folder = config.binding_sites / sugar

    # Path to the new folder where the fixed structures will be saved
    fixed_folder = config.binding_sites / f"{sugar}_fixed_{min_res}"#FIXME:
    fixed_folder.mkdir(exist_ok=True) #FIXME:

    less_than_n_aa = []  # How many structures were excluded
    i = 0  # Index
    structures_keys = {} # To map index with structure
    for path_to_file in structures_folder.iterdir():
        filename = Path(path_to_file.name).stem
        # cmd.delete("all") # delete all
        pm_cmd("delete all")
        # cmd.load(path_to_file) # load path_to_file
        pm_cmd(f"load {path_to_file}")
        # count = cmd.count_atoms("n. CA and polymer") # count_atoms n. CA and polymer
        count = int(pm_cmd('print(cmd.count_atoms("n. CA and polymer"))')[-1])
        # pm_cmd('res = cmd.count_atoms("n. CA and polymer")')[-1]
        # count = int(pm_cmd('print(res)')[-1])
        if count < min_res:
            less_than_n_aa.append(filename)
            continue

        try:
            _, res, num, chain = filename.split("_")
        except ValueError:
            _, res, num, chain, _ = filename.split("_")
        # For some reason, some structures have chains named eg. AaA but when loaded to PyMol
        # the the chain is reffered to just as A.
        if len(chain) > 1:
            chain = chain[0]

        current_sugar = f"/{filename}//{chain}/{res}`{num}"

        pm_cmd(f"select wanted_residues, {current_sugar} or polymer") # select wanted_residues, /1ax1_GAL_2_C//C/GAL`2 or polymer
        pm_cmd("select junk_residues, not wanted_residues") #select junk_residues, not wanted_residues
        pm_cmd("remove junk_residues") 
        pm_cmd("delete junk_residues")

        pm_cmd(f"save {fixed_folder}/{i}_{filename}.pdb") # save path_to_file
        structures_keys[i] = f"{i}_{filename}.pdb"
        i += 1 # Raise the index
        pm_cmd("delete all")

    (config.results_folder / "clusters" / sugar).mkdir(exist_ok=True, parents=True)#FIXME:
    with open(config.results_folder / "clusters" / sugar / f"{sugar}_structures_keys.json", "w") as f:
        json.dump(structures_keys, f, indent=4)
    print(f"number of structures with less than {min_res} AA: ", len(less_than_n_aa))

    return fixed_folder

#FIXME: function description
    # Calculates all against all RMSD (using PyMol rms_cur command) of all structures firstly aligned
    # by their sugar, then aligned by the aminoacids (to find the alignment object - pairs of AA),
    # but without actually moving, so the rms_cur is eventually calculated from their position as is
    # towards the sugar. Results are saved in a form of distance matrix (.npy) and also as .csv file.
def all_against_all_alignment(sugar: str, structures_folder: Path, method: str, config: Config, pm_cmd: Pymol) -> None:
    """
    [TODO:description]

    :param sugar: The sugar for which representative binding sites are being defined
    :param structures_folder: Path to refined binding sites
    :param method: The PyMOL command used to calculate RMSD
    :param config: Config object
    """
    current_sugar_results_path = config.results_folder / "clusters" / sugar / method
    current_sugar_results_path.mkdir(parents=True, exist_ok=True) #FIXME:

    n = len(os.listdir(structures_folder))
    rmsd_values = np.zeros((n, n))

    something_wrong = []

    with open(current_sugar_results_path / f"{sugar}_all_pairs_rmsd_{method}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["structure1", "structure2", "rmsd"])
        for (structure1, structure2) in itertools.combinations(os.listdir(structures_folder), 2):
            try:
                pm_cmd("delete all")
                pm_cmd(f"load {structures_folder}/{structure1}")
                pm_cmd(f"load {structures_folder}/{structure2}")
                # TODO: add path to save the sugar files
                pm_cmd(f"fetch {sugar}")

                filename1 = str(Path(structure1).stem) #FIXME:
                filename2 = str(Path(structure2).stem)

                try:
                    id1, _, res1, num1, chain1 = filename1.split("_")
                except ValueError:
                    id1, _, res1, num1, chain1, _ = filename1.split("_")
                try:
                    id2, _, res2, num2, chain2 = filename2.split("_")
                except ValueError:
                    id2, _, res2, num2, chain2, _ = filename2.split("_")
                # For some reason, some structures has chains named eg. AaA but when loaded to PyMol
                # the the chain is reffered to just as A.
                if len(chain1) > 1:
                    chain1 = chain1[0]
                if len(chain2) > 1:
                    chain2 = chain2[0] 

                sugar1 = f"/{filename1}//{chain1}/{res1}`{num1}"
                sugar2 = f"/{filename2}//{chain2}/{res2}`{num2}"

                pm_cmd(f"select original_sugar1, {sugar1}")
                pm_cmd(f"select original_sugar2, {sugar2}")
                pm_cmd(f"select polymer1, polymer and not {filename2}")
                pm_cmd(f"select polymer2, polymer and not {filename1}")

                pm_cmd(f"align original_sugar1, {sugar}")
                pm_cmd(f"align original_sugar2, {sugar}")
                if method == "align":
                    pm_cmd("align polymer1, polymer2, transform=0, cycles=0, object=aln")
                elif method == "super":
                    pm_cmd("super polymer1, polymer2, transform=0, cycles=0, object=aln") 
                rms = float(pm_cmd("print(cmd.rms_cur('polymer1 & aln', 'polymer2 & aln', matchmaker=-1))")[-1])

                writer.writerow([filename1, filename2, rms])
                rmsd_values[int(id1), int(id2)] = rms 
                rmsd_values[int(id2), int(id1)] = rms

                pm_cmd("delete all") 
            except:
                # Save pairs with which something went wrong
                something_wrong.append((structure1, structure2))

    np.save(current_sugar_results_path / f"{sugar}_all_pairs_rmsd_{method}.npy", rmsd_values)
    with open((current_sugar_results_path / "something_wrong.json"), "w") as f:
        json.dump(something_wrong, f, indent=4)
    # pm_cmd("quit")


def main(sugar: str, method: str, config: Config, pm_cmd: Pymol) -> None:
    # Method: PyMOL command to be used for the calculation of RMSD {align or super}
    fixed_folder = refine_binding_sites(sugar, 5, config, pm_cmd)#FIXME: fixed_folder and structures folder are the same
    all_against_all_alignment(sugar, fixed_folder, method, config, pm_cmd)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--align_method", help = "PyMOL cmd for the calculation of RMSD", type=str, choices=["super", "align"], required=True)

    args = parser.parse_args()

    config = Config.load("config.json")
    pm_cmd = Pymol(gui=True)

    main(args.sugar, args.align_method, config, pm_cmd)
