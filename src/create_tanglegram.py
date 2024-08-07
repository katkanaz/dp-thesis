from argparse import ArgumentParser

import modified_tanglegram
import numpy as np
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd

from config import Config


def create_tanglegram(sugar: str, cluster_method: str, config: Config) -> None:
    """
    Call tanglegram function from an external script, which is modified to show the data as needed for this analysis

    :param sugar: The sugar for which the representative binding site is being defined
    :param cluster_method: Chosen clustering method for matrix computation
    :param config: Config object
    """

    data_super = np.load(config.results_folder / "clusters" / sugar / "super" / f"{sugar}_all_pairs_rmsd_super.npy")
    data_align = np.load(config.results_folder / "clusters" / sugar / "align" / f"{sugar}_all_pairs_rmsd_align.npy")
    # Create densed form of the matrix
    D_super = spd.squareform(data_super)
    D_align = spd.squareform(data_align)

    # Compute the linkage matrix using given cluster_method
    Z_super = sph.linkage(D_super, method=cluster_method)
    Z_align = sph.linkage(D_align, method=cluster_method)

    # NOTE: assuming that this is always the shape of Z_super
    # FIXME: wrong assumption, what is n_data then
    n_data = Z_super.shape[0] + 1
    print(n_data)

    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True, results_folder=config.results_folder)
    fig.savefig(config.tanglegrams / f"tanglegram_{sugar}.svg")
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    #parser.add_argument("n_data", help = "", type=int)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str, choices=["ward", "average", "centroid",
    "single", "complete", "weighted", "median"], required=True)

    args = parser.parse_args()

    config = Config.load("config.json")

    config.tanglegrams.mkdir(exist_ok=True, parents=True)

    create_tanglegram(args.sugar, args.cluster_method, config=config)
    #create_tanglegram("FUC", n_data=618, cluster_method="centroid")
