from argparse import ArgumentParser

import modified_tanglegram
import numpy as np
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd
from logger import setup_logger

from configuration import Config


def create_tanglegram(sugar: str, cluster_method: str, config: Config) -> None:
    """
    Call tanglegram function from an external script, which is modified to show the data as needed for this analysis

    :param sugar: The sugar for which the representative binding site is being defined
    :param cluster_method: Chosen clustering method for matrix computation
    :param config: Config object
    """

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

    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True, results_folder=config.results_dir)
    fig.savefig(config.tanglegrams_dir / f"tanglegram_{sugar}.svg")
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"], required=True)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    config.tanglegrams_dir.mkdir(exist_ok=True, parents=True)

    create_tanglegram(args.sugar, args.cluster_method, config=config)
