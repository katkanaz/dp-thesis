from pathlib import Path
import numpy as np
import modified_tanglegram
import scipy.cluster.hierarchy as sph
import scipy.spatial.distance as spd

from argparse import ArgumentParser

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
TANGLEGRAMS = RESULTS_FOLDER / "tanglegrams"
TANGLEGRAMS.mkdir(exist_ok=True)



def create_tanglegram(sugar: str, cluster_method: str):
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
    n_data = Z_super.shape[0]

    fig = modified_tanglegram.tanglegram(Z_super, Z_align, n_data, sort="step1side", color_by_diff=True)
    fig.savefig(TANGLEGRAMS / f"tanglegram_{sugar}.png")
    

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    #parser.add_argument("n_data", help = "", type=int)
    parser.add_argument("-c", "--cluster_method", help = "Clustering method", type=str, choices=["ward", "average", "centroid",
    "single", "complete", "weighted", "median"], required=True)

    args = parser.parse_args()

    create_tanglegram(args.sugar, args.cluster_method)
    
    #create_tanglegram("FUC", n_data=618, cluster_method="centroid")