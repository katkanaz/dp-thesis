import json

from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd
import matplotlib.pyplot as plt

from argparse import ArgumentParser


RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"

(RESULTS_FOLDER / "clusters").mkdir(exist_ok=True)


def cluster_data(sugar: str, n_clusters: int, cluster_method: str, align_method: str, show=False):
    """
    Perform hierarchical clustering, using the given clustering method (ward, average, centroid,
    single, complete, weighted, median) and create a given number of clusters. 
    """
    
    data = np.load(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{sugar}_all_pairs_rmsd_{align_method}.npy")

    # Create densed form of the matrix
    D = ssd.squareform(data)

    # Compute the linkage matrix using given cluster_method
    Z1 = sch.linkage(D, method=cluster_method) 

    if show:
        # Plot the dendrogram
        fig = plt.figure()
        sch.dendrogram(Z1, color_threshold=6.1)
        plt.show()
        
    # Cut the dendrogram at a desired number of clusters
    labels = sch.fcluster(Z1, t=n_clusters, criterion='maxclust')


    # Save the clusters and IDs of structures belonging to each cluster.
    # 'labels' contains a list of cluster IDs, which indices correspond
    #  to the ID of structure belonging to that cluster.
    index = 0
    clusters = defaultdict(list)
    for label in labels:
        clusters[int(label)].append(index)
        index += 1
    clusters = dict(sorted(clusters.items(), key=lambda x:x[0]))
    with open(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{n_clusters}_{cluster_method}_all_clusters.json", "w") as f:
        json.dump(clusters, f, indent=4)

    # Calculate the representative structures for each cluster, as a structure with the lowest sum of RMSDs
    # with all the other structures from the cluster
    representatives = {}
    print("Průměrné RMSD reprezentativního okolí s ostatními okolími v daném klastru:")
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
        print(f"Cluster {cluster}: {lowest_rmsd_sum / length}")
    
    print("Průměrné RMSD mezi reprezentativními okolími navzájem:")
    for cluster, structure in representatives.items():
        sum = 0
        for cluster2, structure2 in representatives.items():
            sum += data[structure, structure2]
        print(f"Cluster {cluster}: {sum/n_clusters}")


    with open(RESULTS_FOLDER / "clusters" / sugar / align_method / f"{n_clusters}_{cluster_method}_cluster_representatives.json", "w") as f:
        json.dump(representatives, f, indent=4)

if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-s", "--sugar", help = "Three letter code of sugar", type=str)
    parser.add_argument("-n", "--n_clusters", help = "Number of clusters to create", type=int, required=True)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str, choices=["ward", "average", "centroid",
    "single", "complete", "weighted", "median"], required=True)
    parser.add_argument("-a", "--align_method", help = "PyMOL cmd for the calculation of RMSD", type=str, choices=["super", "align"], required=True)
    
    args = parser.parse_args()
    
    cluster_data(args.sugar, args.n_clusters, args.cluster_method, args.align_method, show=True)



    #cluster_data("FUC", 22, "centroid", "super", show=True)
    #cluster_data("FUC", 20, "centroid", "align", show=True)
    