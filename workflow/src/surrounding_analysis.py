"""
Script Name: define_surr_do_sms.py
Description: Define representative surroundings for a given sugar using PQ and PyMOL,
             cluster obtained data and choose representatives to perform structure motif search with.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from datetime import datetime
import logging
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


def main(sugar: str, config: Config, is_unix: bool, perform_align: bool, perform_clustering: bool, number: int, method: str, min_residues: int, max_residues: int, make_dendrogram: bool, color_threshold: Union[float, None] = None) -> None:
    logger.info(f"Running 2nd program with data from {config.run_data_dir.stem} directory")

    with tqdm(total=6 if perform_clustering else 3) as pbar: 
        pbar.set_description("Running PatternQuery")
        run_pq(sugar, config, is_unix)
        pbar.update(1)

        try:
            pbar.set_description("Performing alignment")
            perform_alignment(sugar, perform_align, config, min_residues)
            pbar.update(1)
        except Exception as e:
            logger.error(f"Exception caught: {e}")
            raise e

        if perform_clustering:
            pbar.set_description("Clustering data")
            cluster_data(sugar, number, method, config, make_dendrogram, perform_align, color_threshold)
            pbar.update(1)

            pbar.set_description("Comparing clusters")
            compare_clusters(config, perform_align, number, method)
            pbar.update(1)

            pbar.set_description("Creating tanglegram")
            create_tanglegram(sugar, number, method, config, perform_align)
            pbar.update(1)

        pbar.set_description("Performing structure motif search")
        structure_motif_search(sugar, perform_clustering, number, method, config, max_residues)
        pbar.update(1)


if __name__ == "__main__":
    start_time = datetime.now()

    parser = ArgumentParser()

    parser.add_argument("--config", help="Path to config file", type=str, default="config.json")
    parser.add_argument("-t", "--test_mode", action="store_true",
                        help="Weather to run the whole process in a test mode")
    parser.add_argument("-s", "--sugar", help="The sugar abbreviation", type=str, required=True)
    parser.add_argument("-a", "--perform_align", action="store_true", help="Whether to perform calculation of RMSD using the PyMOL align command as well")
    parser.add_argument("-c", "--perform_clustering", action="store_true", help="Whether to perform data clustering of filtered surroundings")
    parser.add_argument("-n", "--number", help="Number of clusters to create", type=int, default=20)
    parser.add_argument("-m", "--method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"], default="centroid")
    parser.add_argument("--min_residues", help="Minimal number of residues required in a surrounding", type=int, default=5)
    parser.add_argument("--max_residues", help="Maximal number of residues in a surrunding. Required by structure motif search", type=int, default=5)
    parser.add_argument("-d", "--make_dendrogram", action="store_true", help="Whether to create and save the dendrogram")
    parser.add_argument("--color_threshold", type=float, help="Color threshold for dendrogram (default: None)")

    args = parser.parse_args()

    if args.perform_clustering:
        if args.number is None or args.method is None:
            parser.error("-n/--number and -m/--method should only be provided if -c/--perform_clustering is used.")
    else:
        if args.number is not None or args.method is not None:
            parser.error("When using -c/--perform_clustering both -n/--number and -m/--method must be provided.")


    config = Config.load(args.config, args.sugar, True, args)

    setup_logger(config.log_path)
    logger.info(f"Called with the following arguments: {vars(args)}")

    is_unix = system() != "Windows"

    with logging_redirect_tqdm():
        main(args.sugar, config, is_unix, args.perform_align, args.perform_clustering, args.number, args.method, args.min_residues, args.max_residues, args.make_dendrogram, args.color_threshold)

    Config.clear_current_run()

    end_time = datetime.now()
    duration = end_time - start_time
    seconds = duration.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    logger.info(f"Program completed successfully in {int(hours)}h {int(minutes)}m {int(seconds)}s")
