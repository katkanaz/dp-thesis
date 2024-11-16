"""
Script Name: download_and_categorization.py
Description: Download structures with sugars from PDB,
             get all residues that are ligands and filter them. 
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from platform import system

from configuration import Config

from download_files import download_files
from categorize import categorize
from extract_rscc_and_resolution import extract_rscc_and_resolution
from run_mv import run_mv
from plot_graphs import plot_graphs
from graph_analysis import graph_analysis
from remove_o6 import get_ids_and_remove_o6
from filter_ligands import filter_ligands

# TODO: add function that deletes sugar cif files from data/run/sugars
def main(config: Config, is_unix: bool, min_rscc: float, max_rscc: float, min_rmsd: float,
         max_rmsd: float, res: float, rscc: float, rmsd: float, make_graphs: bool = False):

    download_files(config)
    categorize(config)
    extract_rscc_and_resolution(config)
    run_mv(config, is_unix)
    plot_graphs(config)
    graph_analysis(config, min_rscc, max_rscc, min_rmsd, max_rmsd)
    process_and_filter_ligands(config)
        get_ids_and_remove_o6(config)
    filter_ligands(res, rscc, rmsd, config)

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--min_rscc", help="Minimum RSCC used to define graph area", type="float", required=True, default=0.85)
    parser.add_argument("--max_rscc", help="Maximum RSCC used to define graph area", type="float", required=True, default=1.0)
    parser.add_argument("--min_rmsd", help="Minimum RMSD used to define graph area", type="float", required=True, default=2.0)
    parser.add_argument("--max_rmsd", help="Maximum RMSD used to define graph area", type="float", required=True, default=3.0)
    #FIXME: should they have default? how to automate this, it originates in residue graphs?

    args = parser.parse_args()

    config = Config.load("config.json")
    is_unix = system() != "Windows"

    # TODO: Create object to pass arguments
    main(config, is_unix, args.min_rscc, args.max_rscc, args.min_rmsd, args.max_rmsd,
         args.res, args.rscc, args.rmsd, args.make_graphs)
