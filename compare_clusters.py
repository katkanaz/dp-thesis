from argparse import ArgumentParser
import json
from pathlib import Path

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"


def compare_clusters(sugar: str) -> None:
    #TODO: add docs
    """
    How many clusters from align-data correspond to one cluster from super-data, and vice versa.
    """

    with (RESULTS_FOLDER / "clusters" / sugar / "super" / "22_centroid_all_clusters.json").open() as f:
        clusters_super = json.load(f)

    with (RESULTS_FOLDER / "clusters" / sugar / "align" / "20_centroid_all_clusters.json").open() as f:
        clusters_align = json.load(f)
    
    # create dict in a form of {structure: cluster}
    reversed_clusters_align = {}
    for cluster, structures in clusters_align.items():
        reversed_clusters_align.update({structure: cluster for structure in structures})

    # iterate over structures from super clusters and save cluster ids of those structures in align clusters
    overall_spread_from_super = {}
    for cluster, structures in clusters_super.items():
        overall_spread_from_super[cluster] = {reversed_clusters_align[structure] for structure in structures}


    reversed_clusters_super = {}
    for c, ss in clusters_super.items():
        reversed_clusters_super.update({s: c for s in ss})

    overall_spread_from_align = {}
    for c, ss in clusters_align.items():
        overall_spread_from_align[c] = {reversed_clusters_super[s] for s in ss}

    
    print(overall_spread_from_super)
    print(overall_spread_from_align)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)

    args = parser.parse_args()

    compare_clusters(args.sugar)