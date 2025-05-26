"""
Script Name: define_bs_do_sms.py
Description: Define representative binding sites for a given sugar using PQ and PyMOL,
             cluster obtained data and choose representatives to perform structure motif search with.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from platform import system
from typing import Union

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from logger import logger, setup_logger

from configuration import Config

from process_handlers.run_pq import run_pq
from process_handlers.perform_alignment import perform_alignment
from process_handlers.cluster_data import cluster_data
from process_handlers.compare_clusters import compare_clusters
from process_handlers.create_tanglegram import create_tanglegram
from process_handlers.structure_motif_search import structure_motif_search


def main(sugar: str, config: Config, is_unix: bool, perform_align: bool, n_clusters: int, cluster_method: str, make_dendrogram: bool,
         color_threshold: Union[float, None] = None) -> None:
    logger.info(f"Running 2nd program from {config.run_data_dir.stem} directory")
    with tqdm(total=5) as pbar: 
        pbar.set_description("Running PatternQuery")
        run_pq(sugar, config, is_unix)
        pbar.update(1)

        try:
            pbar.set_description("Performing alignment")
            perform_alignment(sugar, perform_align, config)
            pbar.update(1)
        except Exception as e:
            logger.error(f"Exception caught: {e}")
            raise e

        pbar.set_description("Clustering data")
        cluster_data(sugar, n_clusters, cluster_method, config, make_dendrogram, perform_align, color_threshold)
        pbar.update(1)

        pbar.set_description("Comparing clusters")
        compare_clusters(config, perform_align, n_clusters, cluster_method)
        pbar.update(1)

        pbar.set_description("Creating tanglegram")
        create_tanglegram(sugar, n_clusters, cluster_method, config, perform_align)
        pbar.update(1)

        pbar.set_description("Performing structure motif search")
        structure_motif_search(sugar, n_clusters, cluster_method, config)
        pbar.update(1)


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
    with logging_redirect_tqdm():
        main(args.sugar, config, is_unix, args.perform_align, args.n_clusters, args.cluster_method, args.make_dendrogram, args.color_threshold)

    Config.clear_current_run()
