import csv
import json
from pathlib import Path
from collections import defaultdict

from csv import DictReader

import gemmi
import numpy as np
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd
import pandas as pd

import modified_tanglegram


RESULTS_FOLDER = Path(__file__).parent.parent / "results"
DATA_FOLDER = Path(__file__).parent.parent / "data"


def get_pdb_ids_from_pq():
    """
    Gets PDB IDs of structures from PQ results.
    """
    path_to_pq_results = "/my query/patterns"
    structures = set()
    for i in path_to_pq_results.iterdir():
        structures.add(str(i.name).split("_")[0])
    with open((DATA_FOLDER / "pdb_ids_PQ.json"), "w") as f:
        json.dump(list(structures), f, indent=4)


def remove_nonsugar_residues():
    """
    Removes all residues which are not saccharides from the model mmCIF file.
    """
    doc = gemmi.cif.read(str(DATA_FOLDER / "components.cif.gz"))
    for i in range(len(doc) - 1, -1, -1):
        comp_type = doc[i].find_value('_chem_comp.type')
        if "saccharide" not in comp_type.lower():
            del doc[i]
    doc.write_file(str(DATA_FOLDER / "only_sugars.cif"))


def get_rmsd_and_merge():
    """
    Gets RMSDs from MotiveValidator results and merges them with the file with resolutions and RSCC values.
    """
    with open(Path(__file__).parent.parent / f"MotiveValidator_1.1.21.12.14a\\result\\index.json") as f:
        data = json.load(f)
    with open(RESULTS_FOLDER / "validation" / "all_rmsd.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pdb", "name", "num", "chain", "rmsd"])
        for model in data["Models"]:
            for entry in model["Entries"]:
                pdb = entry["Id"].split("_")[0]
                res = str(entry["MainResidue"]).split()
                try:
                    row = [pdb.upper(), res[0], res[1], res[2], str(entry["ModelRmsd"])]
                except:
                    continue
                writer.writerow(row)

    rscc = pd.read_csv(RESULTS_FOLDER / "validation" / "all_rscc_and_resolution.csv")
    rmsd = pd.read_csv(RESULTS_FOLDER / "validation" / "all_rmsd.csv")

    merged = rscc.merge(rmsd, on=["pdb", "name", "num", "chain"])
    merged.to_csv(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", index=False)


def filter_ligands(max_resolution, min_rscc, max_rmsd):
    """
    Filters ligands.json to contain only those structures whose overall resolution
    is better than <max_resolution> and residues with RSCC higher than <min_rscc>
    and rmsd lower than <max_rmsd>
    """
    with open(RESULTS_FOLDER / "categorization" / "ligands.json", "r") as f:
        ligands = json.load(f)
    print("number of structures before filtering: ", len(ligands.keys()))
    count = 0
    for pdb, residues in ligands.items():
        count += len(residues)
    print("number of residues before filtering: ", count)

    # save the pdb id of structures with good resolution, because not all structures has resolution
    # available and we want to continue just with those with resolution
    good_structures = set()
    with open(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if float(row["resolution"]) <= max_resolution and row["type"] == "ligand":
                good_structures.add(row["pdb"])
    
    # delete those structures which are not in good_structures
    delete_strucutres = [pdb for pdb in ligands.keys() if pdb not in good_structures]
    for key in delete_strucutres:
        del ligands[key]

    # get individual resiudes which have bad rscc or rmsd
    delete_residues = defaultdict(list)
    with open(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", "r") as f:
        rscc_rmsd = DictReader(f)
        for row in rscc_rmsd:
            if row["type"] == "ligand" and (float(row["rmsd"]) > max_rmsd or float(row["rscc"]) < min_rscc):
                delete_residues[row["pdb"]].append({"name": row["name"], "num" : row["num"], "chain": row["chain"]})
    
    # save structures from which all residues were deleted
    delete_empty_structures = set()
    for pdb, residues in ligands.items():
        if pdb in delete_residues:
            for residue in delete_residues[pdb]:
                residues.remove(residue)
            if len(residues) == 0:
                delete_empty_structures.add(pdb)

    for key in delete_empty_structures:
        del ligands[key]

    print("number of structures after filtering: ", len(ligands.keys()))
    count = 0
    for pdb, residues in ligands.items():
        count += len(residues)
    print("number of residues after filtering: ", count)

    with open(RESULTS_FOLDER / "categorization" / "filtered_ligands.json", "w") as f:
        json.dump(ligands, f, indent=4)


def get_average_rmsd_of_peaks():
    """
    This is for finding average rmsd of those two peaks appearing in the histograms.
    """
    read_path = RESULTS_FOLDER / "merged_rscc_rmsd.csv"
    df = pd.read_csv(read_path)
    data = df[df["name"] == "BGC"]
    filtered_df1 = data[data["rmsd"] <= 0.4]
    filtered_df2 = data[data["rmsd"] > 0.4]
    filtered_df3 = filtered_df2[filtered_df2["rmsd"] < 0.7]
    average1 = filtered_df1["rmsd"].mean()
    average2 = filtered_df3["rmsd"].mean()

    print(average1, average2)


def analyze_graph(min_rscc, max_rscc, min_rmsd, max_rmsd, name=None):
    """
    Prints what kind of sugars are in the defined area on the graph.
    """
    with open(RESULTS_FOLDER / "validation" /  "merged_rscc_rmsd.csv") as f:
        rscc_rmsd = DictReader(f)
        sugars = set()
        for row in rscc_rmsd:
            if float(row["rmsd"]) >= min_rmsd and float(row["rmsd"]) <= max_rmsd and float(row["rscc"]) >= min_rscc and float(row["rscc"]) <= max_rscc:
                sugars.add(row["name"])
                print(row)
    print(sugars)
    print(len(sugars))


def get_pdb_ids_with_rscc():
    """
    Get PDB IDs of structures for which residues there are the RSCC values.
    """
    with open(RESULTS_FOLDER / "validation" / "all_rscc_and_resolution.csv") as f:
        rscc = DictReader(f)
        pdb_ids = set()
        for row in rscc:
            pdb_ids.add(row["pdb"])
    with open("pdbs_with_rscc_and_resolution.json", "w") as f:
        json.dump(list(pdb_ids))


def remove_O6():
    """
    Removes atom O6 of NAG, GAL, MAN, GLC and BGC from the structures.
    """
    result = DATA_FOLDER / "mmCIF_bez_O6"
    result.mkdir(exist_ok=True)
    with open(RESULTS_FOLDER / "validation" / "pdbs_with_rscc_and_resolution.json") as f:
        pdb_ids_of_interest = json.load(f)
    for pdb in pdb_ids_of_interest:
        with (DATA_FOLDER / "mmCIF_files"/ f"{pdb.lower()}.cif").open() as f:
            file = f.readlines()
        with (result / f"{pdb.lower()}.cif").open("w") as f:
            for line in file:
                if line.startswith("HETATM"):
                    if "MAN" in line or "NAG" in line or "GAL" in line or "GLC" in line or "BGC" in line:
                        if "O6" in line:
                            continue
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                else:
                    f.write(line)


def compare_clusters():
    """
    Tells how many clusters from align-data correspond to one cluster from super-data, and vice versa
    """
    with (RESULTS_FOLDER / "clusters" / "FUC" / "super" / "22_centroid_all_clusters.json").open() as f:
        clusters_super = json.load(f)

    with (RESULTS_FOLDER / "clusters" / "FUC" / "align" / "20_centroid_all_clusters.json").open() as f:
        clusters_align = json.load(f)
    
    # create dict in a form of {structure: cluster}
    reversed_clusters_align = {}
    for cluster, structures in clusters_align.items():
        reversed_clusters_align.update({structure: cluster for structure in structures})

    # iterate over structures from super clusters and save cluster ids of those structures in align clusters
    overall_rozptyl_from_super = {}
    for cluster, structures in clusters_super.items():
        overall_rozptyl_from_super[cluster] = {reversed_clusters_align[structure] for structure in structures}


    reversed_clusters_super = {}
    for c, ss in clusters_super.items():
        reversed_clusters_super.update({s: c for s in ss})

    overall_rozptyl_from_align = {}
    for c, ss in clusters_align.items():
        overall_rozptyl_from_align[c] = {reversed_clusters_super[s] for s in ss}

    
    print(overall_rozptyl_from_super)
    print(overall_rozptyl_from_align)


def create_tanglegram():
    """
    Calls the external script tanglegram, which is modified to show the data as needed for this analysis.
    """
    sugar = "FUC"
    n_data = 620
    cluster_method = "centroid"

    data_super = np.load(RESULTS_FOLDER / "clusters" / sugar / "super" / f"{sugar}_all_pairs_rmsd.npy")
    data_align = np.load(RESULTS_FOLDER / "clusters" / sugar / "align" / f"{sugar}_all_pairs_rmsd.npy")
    # Create densed form of the matrix
    D_super = spd.squareform(data_super)
    D_align = spd.squareform(data_align)

    # Compute the linkage matrix using given cluster_method
    Z_super = sph.linkage(D_super, method=cluster_method)
    Z_align = sph.linkage(D_align, method=cluster_method)


    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True)
    fig.savefig("tanglegram")