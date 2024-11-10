"""
Script Name: download_and_categorization.py
Description: Download structures with sugars from PDB and perform sugar categorization.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from pathlib import Path
from platform import system

from config import Config

from download_files import download_files
from categorize import categorize
from extract_rscc_and_resolution import extract_rscc_and_resolution
from run_mv import run_mv
from plot_graphs import plot_graphs
from graph_analysis import graph_analysis
from process_and_filter_ligands import process_and_filter_ligands

# TODO: add function that deletes sugar cif files from data/run/sugars
def main(config: Config, is_unix: bool, min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float):#TODO: is main appropriate name?

    # download_files(config)
    categorize(config)
    extract_rscc_and_resolution(config)
    run_mv(config, is_unix)
    plot_graphs(config)
    graph_analysis(config, min_rscc, max_rscc, min_rmsd, max_rmsd)
    process_and_filter_ligands(config)

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--min_rscc", help="Minimum RSCC used to define graph area", type="float", required=True, default=0.85)
    parser.add_argument("--max_rscc", help="Maximum RSCC used to define graph area", type="float", required=True, default=1.0)
    parser.add_argument("--min_rmsd", help="Minimum RMSD used to define graph area", type="float", required=True, default=2.0)
    parser.add_argument("--max_rmsd", help="Maximum RMSD used to define graph area", type="float", required=True, default=3.0)
    #FIXME: where do the values come from

    args = parser.parse_args()

    config = Config.load("config.json")
    is_unix = system() != "Windows"

    main(config, is_unix, args.min_rscc, args.max_rscc, args.min_rmsd, args.max_rmsd)
