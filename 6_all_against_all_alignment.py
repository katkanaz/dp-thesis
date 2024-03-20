import csv
import itertools
import json
import os
from pathlib import Path

import numpy as np
from pymol import cmd

from argparse import ArgumentParser


RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"


def refine_binding_sites(sugar: str, min_res: int):
    """
    Filters the binding sites obtained by PQ to contain only the target sugar and at least <min_res> AA
    and gives the filtered structures unique ID, which will be used as an index for creating the
    rmsd matrix.
    """
    # Path to the folder containing the PDB structures from PQ
    structures_folder = RESULTS_FOLDER / "binding_sites" / sugar

    # Path to the new folder where the fixed structures will be saved
    fixed_folder = RESULTS_FOLDER / "binding_sites" / f"{sugar}_fixed_{min_res}"
    fixed_folder.mkdir(exist_ok=True)

    less_than_n_aa = []  # just to know how many structures were excluded
    i = 0  # index
    structures_keys = {} # to map index with structure
    for path_to_file in structures_folder.iterdir():
        filename = Path(path_to_file.name).stem
        cmd.delete("all")
        cmd.load(path_to_file)
        count = cmd.count_atoms("n. CA and polymer")
        if count < min_res:
            less_than_n_aa.append(filename)
            continue
        
        try:
            pdb, res, num, chain = filename.split("_")
        except ValueError:
            pdb, res, num, chain, tag = filename.split("_")
        # For some reason, some structures have chains named eg. AaA but when loaded to PyMol
        # the the chain is reffered to just as A.
        if len(chain) > 1:
            chain = chain[0]

        current_sugar = f"/{filename}//{chain}/{res}`{num}"

        cmd.select("wanted_residues", f"{current_sugar} or polymer")
        cmd.select("junk_residues", f"not wanted_residues")
        cmd.remove("junk_residues") 
        cmd.delete("junk_residues")

        cmd.save(f"{fixed_folder}/{i}_{filename}.pdb")
        structures_keys[i] = f"{i}_{filename}.pdb"
        i += 1 # raise the index
        cmd.delete("all")

    (RESULTS_FOLDER / "clusters" / sugar).mkdir(exist_ok=True, parents=True)
    with open(RESULTS_FOLDER / "clusters" / sugar / f"{sugar}_structures_keys.json", "w") as f:
        json.dump(structures_keys, f, indent=4)
    print(f"number of structures with less than {min_res} AA: ", len(less_than_n_aa))

    return fixed_folder


def all_against_all_alignment(sugar: str, structures_folder: Path, method: str):
    """
    Calculates all against all RMSD (using PyMol rms_cur command) of all structures firstly aligned
    by their sugar, then aligned by the aminoacids (to find the alignment object - pairs of AA),
    but without actually moving, so the rms_cur is eventually calculated from their position as is
    towards the sugar. Results are saved in a form of distance matrix (.npy) and also as .csv file.
    """
    current_sugar_results_path = RESULTS_FOLDER / "clusters" / sugar / method
    current_sugar_results_path.mkdir(parents=True, exist_ok=True)

    n = len(os.listdir(structures_folder))
    rmsd_values = np.zeros((n, n))

    something_wrong = []

    with open(current_sugar_results_path / f"{sugar}_all_pairs_rmsd_{method}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["structure1", "structure2", "rmsd"])
        for (structure1, structure2) in itertools.combinations(os.listdir(structures_folder), 2):
            try:
                cmd.delete("all")
                cmd.load(f"{structures_folder}/{structure1}")
                cmd.load(f"{structures_folder}/{structure2}")
                cmd.fetch(sugar)

                filename1 = str(Path(structure1).stem)
                filename2 = str(Path(structure2).stem)

                try:
                    id1, pdb1, res1, num1, chain1 = filename1.split("_")
                except ValueError:
                    id1, pdb1, res1, num1, chain1, tag1 = filename1.split("_")
                try:
                    id2, pdb2, res2, num2, chain2 = filename2.split("_")
                except ValueError:
                    id2, pdb2, res2, num2, chain2, tag2 = filename2.split("_")
                # For some reason, some structures has chains named eg. AaA but when loaded to PyMol
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
                if method == "align":
                    cmd.align("polymer1", "polymer2", transform=0, cycles=0, object="aln")
                elif method == "super":
                    cmd.super("polymer1", "polymer2", transform=0, cycles=0, object="aln") 
                rms = float(cmd.rms_cur("polymer1 & aln", "polymer2 & aln", matchmaker=-1))

                writer.writerow([filename1, filename2, rms])
                rmsd_values[int(id1), int(id2)] = rms 
                rmsd_values[int(id2), int(id1)] = rms

                cmd.delete("all") 
            except:
                # save pairs with which something went wrong
                something_wrong.append((structure1, structure2))

    np.save(current_sugar_results_path / f"{sugar}_all_pairs_rmsd_{method}.npy", rmsd_values)
    with open((current_sugar_results_path / "something_wrong.json"), "w") as f:
        json.dump(something_wrong, f, indent=4)
    cmd.quit()


def main(sugar: str, method: str):
    # method: PyMOL command to be used for the calculation of RMSD {align or super}
    fixed_folder = refine_binding_sites(sugar, 5)
    all_against_all_alignment(sugar, fixed_folder, method)


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--align_method", help = "PyMOL cmd for the calculation of RMSD", type=str, choices=["super", "align"], required=True)
    
    args = parser.parse_args()
    
    main(args.sugar, args.align_method)
