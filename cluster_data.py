from argparse import ArgumentParser
from collections import defaultdict
import csv
import json
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
(RESULTS_FOLDER / "clusters").mkdir(exist_ok=True, parents=True)

DENDROGRAMS = Path(__file__).parent.parent / "images" / "dendrograms"
DENDROGRAMS.mkdir(exist_ok=True, parents=True)

DEBUG_DIR = Path(__file__).parent.parent / "debug"
DEBUG_DIR.mkdir(exist_ok=True, parents=True)


def cluster_data(sugar: str, n_clusters: int, cluster_method: str, 
                 align_method: str, make_dendrogram: bool = False,
                 color_threshold: Union[float, None] = None) -> None:
    """Perform hierarchical clustering, using the specified clustering 
        method and create the given number of clusters.

    :param str sugar: The sugar for which representative binding sites are being defined
    :param int n_clusters: The number of clusters to create
    :param str cluster_method: The desired method of clustering. Valid options
                                include "ward", "average", "centroid", "single",
                                "complete", "weighted", "median"
    :param str align_method: The PyMOL command that was used for alignment
    :param bool make_dendrogram: Whether to create and save the dendrogram plot, defaults to False
    :param Union[float, None] color_threshold: The color threshold for the dendrogram plot, defaults to None
    """
    
    data = np.load(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{sugar}_all_pairs_rmsd_{align_method}.npy")
    # print(data) #TODO: remove

    # Create densed form of the matrix
    D = ssd.squareform(data)
    # print(D) #TODO: remove

    # Calculate the linkage matrix using given cluster_method
    Z1 = sch.linkage(D, method=cluster_method)
    # print(Z1) #TODO: remove

    #TODO: try to calculate the num of clusters from matrix with given threshold
    # something times threshold - 1
    dendro_sugar_folder = DENDROGRAMS / sugar
    dendro_sugar_folder.mkdir(exist_ok=True, parents=True)

    if make_dendrogram:
        # Plot the dendrogram
        plt.figure(figsize=(12, 8))
        #TODO: add labels to axis
        dendr = sch.dendrogram(Z1, color_threshold=color_threshold)
        if color_threshold is None:
            print(f"Color threshold is: {0.7*max(Z1[:,2])}")

        # Save the figure to the sugar folder
        if color_threshold is None:
            filename = f"{n_clusters}_{cluster_method}_{align_method}.svg"
        else:
            filename = f"{n_clusters}_{cluster_method}_{align_method}_{color_threshold}.svg"
        fig_path = dendro_sugar_folder / filename
        # plt.show()#TODO: remove
        plt.savefig(fig_path, dpi=300)
        plt.close()

    
    #NOTE: dict returned by .dendrogram()
    with open(DEBUG_DIR / f"dendrogram_dict.json", "w") as f:
        json.dump(dendr, f, indent=4)
    

    # Cut the dendrogram at the desired number of clusters
    labels = sch.fcluster(Z1, t=n_clusters, criterion="maxclust")
    # print(labels) #TODO: remove

    #TODO: reword
    # Save the clusters and the IDs of the structures belonging to each
    # cluster. "labels" contains a list of cluster IDs whose indices
    # correspond to the IDs of the structures belonging to the cluster.
    index = 0
    clusters = defaultdict(list)
    for label in labels:
        clusters[int(label)].append(index)
        index += 1
    clusters = dict(sorted(clusters.items(), key=lambda x:x[0]))
    with open(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{n_clusters}_{cluster_method}_all_clusters.json", "w") as f:
        json.dump(clusters, f, indent=4)

    # Calculate the representative structure for each cluster
    # as the structure with the lowest sum of RMSD with all other
    # structures in the cluster
    #TODO: extract to function
    representatives = {}
    average_rmsds = {}

    for cluster, structures in clusters.items():
            lowest_rmsd_sum = np.inf
            for i in structures:
                sum = 0
                for j in structures:
                    sum += data[i, j]
                if sum < lowest_rmsd_sum:
                    lowest_rmsd_sum = sum
                    representative_structure = i
            length = len(structures)
            representatives[cluster] = representative_structure
            average_rmsds[cluster] = [lowest_rmsd_sum / length]

    for cluster, structure in representatives.items():
            sum = 0
            for cluster2, structure2 in representatives.items():
                sum += data[structure, structure2]
            average_rmsds[cluster].append(sum/n_clusters)

    with open(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{n_clusters}_{cluster_method}_average_rmsds.csv",
              "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["# intra_avg_rmsd: Average RMSD of the representative surroundings with other surroundings in the respective cluster"])
        writer.writerow(["# inter_avg_rmsd: Average RMSD between the representative surroundings"])
        writer.writerow(["cluster", "intra_avg_rmsd", "inter_avg_rmsd"])

        for cluster, rmsds in average_rmsds.items():
            writer.writerow([cluster, rmsds[0], rmsds[1]])


    with open(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{n_clusters}_{cluster_method}_cluster_representatives.json", "w") as f:
        json.dump(representatives, f, indent=4)

if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-n", "--n_clusters", help="Number of clusters to create", type=int)
    parser.add_argument("-c", "--cluster_method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"],
                        required=True)
    parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", type=str,
                        choices=["super", "align"], required=True)
    parser.add_argument("-d", "--make_dendrogram", action="store_true", help="Whether to create and save the dendrogram")
    parser.add_argument("-t", "--color_threshold", type=float, help="Color threshold for dendrogram (default: None)")
    
    args = parser.parse_args()
    
    #TODO: make number of clusters optional
    cluster_data(args.sugar, args.n_clusters, args.cluster_method, args.align_method, args.make_dendrogram, args.color_threshold)
    