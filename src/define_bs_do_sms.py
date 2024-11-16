"""
Script Name: define_bs_do_sms.py
Description: Define representative binding sites for a given sugar using PQ and PyMOL,
cluster obtained data and choose representatives to perform structure motif search with.
Author: Kateřina Nazarčuková
"""

#NOTE: what if a want to run the scripts one by one, just commnet it?
#TODO: do i need all the libs from other scripts imported or just the ones used in this specidic script
from argparse import ArgumentParser
from pathlib import Path
from platform import system
from typing import Union

from configuration import Config

from run_pq import run_pq #TODO: should the main functions have documentation, in this way it wont be readable what it does
from perform_alignment import perform_alignment
from cluster_data import cluster_data
from compare_clusters import compare_clusters
from create_tanglegram import create_tanglegram
from structure_motif_search import structure_motif_search

#TODO: is union not in python 3.8
def main(sugar: str, align_method: str, n_clusters: int, cluster_method: str, make_dendrogram: bool,
         color_threshold: Union[float, None] = None, config: Config, is_unix: bool):
    run_pq(sugar, config, is_unix)
    perform_alignment(sugar, align_method, config)
    cluster_data(sugar, n_clusters, cluster_method, align_method, config, make_dendrogram, color_threshold)
    compare_clusters()
    create_tanglegram()
    structure_motif_search()


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="The sugar abbreviation", type="str", required=True)
    parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", choices=["super", "align"],
                        type="str", required=True)
    parser.add_argument("-n", "--n_clusters", help="Number of clusters to create", type=int)
    parser.add_argument("-c", "--cluster_method", help="Clustering method", type=str,
                        choices=["ward", "average", "centroid", "single", "complete", "weighted", "median"],
                        required=True)
    parser.add_argument("-d", "--make_dendrogram", action="store_true", help="Whether to create and save the dendrogram")
    parser.add_argument("-t", "--color_threshold", type=float, help="Color threshold for dendrogram (default: None)")

    args = parser.parse_args()

    config = Config.load("config.json")#TODO: fix confing for python 3.8
    is_unix = system() != "Windows"
    #TODO: are positional?

    #TODO: make the number of clusters optional
    main(args.sugar, args.align_method, args.n_clusters, args.cluster_method, args.make_dendrogram, args.color_threshold, config, is_unix)



