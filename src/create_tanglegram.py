from argparse import ArgumentParser
from pathlib import Path

import modified_tanglegram
import numpy as np
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
TANGLEGRAMS = Path(__file__).parent.parent / "images" / "tanglegrams"
TANGLEGRAMS.mkdir(exist_ok=True, parents=True)


def create_tanglegram(sugar: str, cluster_method: str) -> None:
    #TODO: add docs
    """
    Call the external script tanglegram, which is modified to show the data as needed for this analysis.
    """

    data_super = np.load(RESULTS_FOLDER / "clusters" / sugar / "super" / f"{sugar}_all_pairs_rmsd_super.npy")
    data_align = np.load(RESULTS_FOLDER / "clusters" / sugar / "align" / f"{sugar}_all_pairs_rmsd_align.npy")
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

    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True)
    fig.savefig(TANGLEGRAMS / f"tanglegram_{sugar}.svg")
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    #parser.add_argument("n_data", help = "", type=int)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str, choices=["ward", "average", "centroid",
    "single", "complete", "weighted", "median"], required=True)

    args = parser.parse_args()

    create_tanglegram(args.sugar, args.cluster_method)
    
    #create_tanglegram("FUC", n_data=618, cluster_method="centroid")