"""
Script Name: define_bs_do_sms.py
Description: Define representative binding sites for a given sugar using PQ and PyMOL,
             cluster obtained data and choose representatives to perform structure motif search with.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from platform import system
from typing import Union
from logger import setup_logger

from configuration import Config

from modules.run_pq import run_pq
from modules.perform_alignment import perform_alignment
from modules.cluster_data import cluster_data
from modules.compare_clusters import compare_clusters
from modules.create_tanglegram import create_tanglegram
from modules.structure_motif_search import structure_motif_search


def main(sugar: str, config: Config, is_unix: bool, perform_align: bool, n_clusters: int, cluster_method: str, make_dendrogram: bool,
         color_threshold: Union[float, None] = None) -> None:
    run_pq(sugar, config, is_unix)
    perform_alignment(sugar, perform_align, config)
    cluster_data(sugar, n_clusters, cluster_method, config, make_dendrogram, perform_align, color_threshold)
    compare_clusters(config, perform_align)
    create_tanglegram(sugar, n_clusters, cluster_method, config, perform_align)
    structure_motif_search(config)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="The sugar abbreviation", type=str, required=True)
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")
    parser.add_argument("-n", "--n_clusters", help="Number of clusters to create", type=int)
    parser.add_argument("-c", "--cluster_method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"],
                        required=True)
    parser.add_argument("-d", "--make_dendrogram", action="store_true", help="Whether to create and save the dendrogram")
    parser.add_argument("-t", "--color_threshold", type=float, help="Color threshold for dendrogram (default: None)")

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    is_unix = system() != "Windows"

    #TODO: Make the number of clusters optional
    main(args.sugar, config, is_unix, args.perform_align, args.n_clusters, args.cluster_method, args.make_dendrogram, args.color_threshold)

    Config.clear_current_run()
