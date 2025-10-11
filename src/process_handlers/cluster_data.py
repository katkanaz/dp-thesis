"""
Script Name: cluster_data.py
Description: Perform hierarchical clustering and create given number of clusters.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from collections import defaultdict
import csv
import json
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd
from logger import logger, setup_logger

from configuration import Config


def perform_data_clustering(sugar: str, number: int, method: str, 
                 align_method: str, config: Config, make_dendrogram: bool,
                 color_threshold: Union[float, None] = None) -> None:
    """
    Perform hierarchical clustering, using the specified clustering 
    method and create the given number of clusters.

    :param sugar: The sugar for which representative binding sites are being defined
    :param number: The number of clusters to create
    :param method: The desired method of clustering. Valid options
                            include "ward", "average", "centroid", "single",
                            "complete", "weighted", "median"
    :param align_method: The PyMOL command that was used for alignment
    :param make_dendrogram: Whether to create and save the dendrogram plot, defaults to False
    :param color_threshold: The color threshold for the dendrogram plot, defaults to None
    """

    logger.info(f"Clustering data from {align_method}")
    # FIXME:
    config.dendrograms_dir.mkdir(exist_ok=True, parents=True)

    data = np.load(config.clusters_dir / align_method / f"{sugar}_all_pairs_rmsd_{align_method}.npy")

    # Create densed form of the matrix
    D = ssd.squareform(data)

    # Calculate the linkage matrix using given cluster_method
    Z1 = sch.linkage(D, method=method)

    # TODO: Try to calculate the num of clusters from matrix with given threshold
    # something times threshold - 1
    dendro_sugar_folder = config.dendrograms_dir
    dendro_sugar_folder.mkdir(exist_ok=True, parents=True)

    if make_dendrogram:
        # Plot the dendrogram
        plt.figure(figsize=(12, 8))
        sch.dendrogram(Z1, color_threshold=color_threshold, no_labels=True)
        plt.xlabel("Surroundings", fontsize=20)
        plt.ylabel("RMSD", fontsize=20)
        if color_threshold is None:
            logger.info(f"Color threshold is: {0.7*max(Z1[:,2])}")

        # Save the figure to the sugar folder
        if color_threshold is None:
            filename = f"{number}_{method}_{align_method}.svg"
        else:
            filename = f"{number}_{method}_{align_method}_{color_threshold}.svg"
        fig_path = dendro_sugar_folder / filename
        plt.savefig(fig_path, dpi=300)
        plt.close()

    # Cut the dendrogram at the desired number of clusters
    labels = sch.fcluster(Z1, t=number, criterion="maxclust")

    # Save the clusters and the IDs of the structures belonging to each
    # cluster. "labels" contains a list of cluster IDs whose indices
    # correspond to the IDs of the structures belonging to the cluster.
    index = 0
    clusters = defaultdict(list)
    for label in labels:
        clusters[int(label)].append(index)
        index += 1
    clusters = dict(sorted(clusters.items(), key=lambda x:x[0]))
    with open(config.clusters_dir / align_method / f"{number}_{method}_all_clusters.json", "w") as f:
        json.dump(clusters, f, indent=4)

    # Calculate the representative structure for each cluster
    # as the structure with the lowest sum of RMSD with all other
    # structures in the cluster
    representatives = {}
    average_rmsds = {}

    for cluster, structures in clusters.items():
        lowest_rmsd_sum = np.inf
        representative_structure = None
        for i in structures:
            sum = 0
            for j in structures:
                sum += data[i, j]
                if sum < lowest_rmsd_sum:
                    lowest_rmsd_sum = sum
                    representative_structure = i
            length = len(structures)
            assert representative_structure is not None, "For every cluster there should be a representative surrounding"
            representatives[cluster] = representative_structure
            average_rmsds[cluster] = [lowest_rmsd_sum / length]

    for cluster, structure in representatives.items():
        sum = 0
        for _, structure2 in representatives.items():
            sum += data[structure, structure2]
            average_rmsds[cluster].append(sum/number)

    with open(config.clusters_dir / align_method / f"{number}_{method}_average_rmsds.csv",
              "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["# intra_avg_rmsd: Average RMSD of the representative surroundings with other surroundings in the respective cluster"])
        writer.writerow(["# inter_avg_rmsd: Average RMSD between the representative surroundings"])
        writer.writerow(["cluster", "intra_avg_rmsd", "inter_avg_rmsd"])

        for cluster, rmsds in average_rmsds.items():
            writer.writerow([cluster, rmsds[0], rmsds[1]])


    with open(config.clusters_dir / align_method / f"{number}_{method}_cluster_representatives.json", "w") as f:
        json.dump(representatives, f, indent=4)


def cluster_data(sugar: str, number: int, method: str, config: Config, make_dendrogram: bool, perform_align: bool,
                 color_threshold: Union[float, None] = None) -> None:
    perform_data_clustering(sugar, number, method, "super", config, make_dendrogram, color_threshold) 
    if perform_align:
        perform_data_clustering(sugar, number, method, "align", config, make_dendrogram, color_threshold) 
        

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-n", "--number", help="Number of clusters to create", type=int, default=20, required=True)
    parser.add_argument("-m", "--method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"],
                        required=True, default="centroid")
    parser.add_argument("-d", "--make_dendrogram", action="store_true", help="Whether to create and save the dendrogram")
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")
    parser.add_argument("-t", "--color_threshold", type=float, help="Color threshold for dendrogram (default: None)")

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True, args)

    setup_logger(config.log_path)

    cluster_data(args.sugar, args.number, args.method, config, args.make_dendrogram, args.perform_align, args.color_threshold)
