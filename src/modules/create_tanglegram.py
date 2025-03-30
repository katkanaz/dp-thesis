"""
Script Name: create_tanglegram.py
Description: Create tanglegram
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser

import modified_tanglegram
import numpy as np
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd
from ..logger import logger, setup_logger

from ..configuration import Config


def create_tanglegram(sugar: str, n_clusters: int, cluster_method: str, config: Config, perform_align: bool) -> None:
    """
    Call tanglegram function from an external script, which is modified to show the data as needed for this analysis

    :param sugar: The sugar for which the representative binding site is being defined
    :param cluster_method: Chosen clustering method for matrix computation
    :param config: Config object
    """

    if not perform_align:
        logger.info("Align was not performed - cannot make tanglegram!")
        return

    logger.info("Creating tanglegram")
    config.tanglegrams_dir.mkdir(exist_ok=True, parents=True)

    data_super = np.load(config.clusters_dir / "super" / f"{sugar}_all_pairs_rmsd_super.npy")
    data_align = np.load(config.clusters_dir / "align" / f"{sugar}_all_pairs_rmsd_align.npy")

    # Create densed form of the matrix
    D_super = spd.squareform(data_super)
    D_align = spd.squareform(data_align)

    # Compute the linkage matrix using given cluster_method
    Z_super = sph.linkage(D_super, method=cluster_method)
    Z_align = sph.linkage(D_align, method=cluster_method)

    # Total number of binding sites for given sugar
    n_data = Z_super.shape[0] + 1

    path_to_file = config.clusters_dir / "super" / f"{n_clusters}_{cluster_method}_all_clusters.json" # FIXME:
    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True, results_folder=path_to_file)
    fig.savefig(config.tanglegrams_dir / f"tanglegram_{sugar}.svg")
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-n", "--n_clusters", help="Number of clusters to create", type=int)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"], required=True)
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    create_tanglegram(args.sugar, args.n_clusters, args.cluster_method, config, args.perform_align)
