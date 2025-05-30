"""
Script Name: compare_clusters.py
Description: Compare clusters from align and super data.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
from logger import logger, setup_logger

from configuration import Config


def compare_clusters(config: Config, perform_align: bool, n_clusters: int, cluster_method: str) -> None:
    """
    How many clusters from align-data correspond to one cluster from super-data, and vice versa

    :param sugar: The sugar for which the representative binding site is being defined
    :param config: Config object
    """

    if not perform_align:
        logger.info("Align was not performed - cannot compare align and super clusters!")
        return

    logger.info("Comparing clusters")

    with (config.clusters_dir / "super" / f"{n_clusters}_{cluster_method}_all_clusters.json").open() as f:
        clusters_super = json.load(f)

    with (config.clusters_dir / "align" / f"{n_clusters}_{cluster_method}_all_clusters.json").open() as f:
        clusters_align = json.load(f)

    # Create dict in a form of {structure: cluster}
    reversed_clusters_align = {}
    for cluster, structures in clusters_align.items():
        reversed_clusters_align.update({structure: cluster for structure in structures})

    # Iterate over structures from super clusters and save cluster ids of those structures in align clusters
    overall_spread_from_super = {}
    for cluster, structures in clusters_super.items():
        overall_spread_from_super[cluster] = {reversed_clusters_align[structure] for structure in structures}


    reversed_clusters_super = {}
    for c, ss in clusters_super.items():
        reversed_clusters_super.update({s: c for s in ss})

    overall_spread_from_align = {}
    for c, ss in clusters_align.items():
        overall_spread_from_align[c] = {reversed_clusters_super[s] for s in ss}

    logger.info(f"Overall spread from super: {overall_spread_from_super}")
    logger.info(f"Overall spread from align: {overall_spread_from_align}")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")
    parser.add_argument("-n", "--n_clusters", help="Number of clusters to create", type=int)
    parser.add_argument("-m", "--cluster_method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"],
                        required=True)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    compare_clusters(config, args.perform_align, args.n_clusters, args.cluster_method)
