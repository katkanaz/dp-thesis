"""
Script Name: download_and_categorization.py
Description: Download structures with sugars from PDB,
             get all residues that are ligands and filter them. 
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from platform import system

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from logger import setup_logger

from configuration import Config

from process_handlers.download_files import download_files
from process_handlers.categorize import categorize
from process_handlers.alternative_conformations import create_separate_mmcifs
# from process_handlers.alternative_conformations import mock_altloc_separation
from process_handlers.extract_rscc_and_resolution import extract_rscc_and_resolution
from process_handlers.run_mv import run_mv
from process_handlers.plot_graphs import plot_graphs
from process_handlers.graph_analysis import graph_analysis
from process_handlers.remove_o6 import get_ids_and_remove_o6
from process_handlers.filter_ligands import filter_ligands


def main(config: Config, is_unix: bool, min_rscc: float, max_rscc: float, min_rmsd: float,
         max_rmsd: float, res: float, rscc: float, rmsd: float, make_graphs: bool,
         test_mode: bool) -> None:

    with tqdm(total=9 if make_graphs else 6) as pbar: 
        pbar.set_description("Downloading files")
        download_files(config, test_mode)
        pbar.update(1)

        pbar.set_description("Categorizing sugars")
        categorize(config)
        pbar.update(1)

        pbar.set_description("Separating alternative conformations")
        create_separate_mmcifs(config)
        # mock_altloc_separation(config)
        pbar.update(1)

        pbar.set_description("Extracting RSCC and resolution")
        extract_rscc_and_resolution(config)
        pbar.update(1)

        pbar.set_description("Running MotiveValidator")
        run_mv(config, is_unix)
        pbar.update(1)

        if make_graphs:
            pbar.set_description("Plotting graphs")
            plot_graphs(config)
            pbar.update(1)

            pbar.set_description("Analysing graphs")
            graph_analysis(config, min_rscc, max_rscc, min_rmsd, max_rmsd)
            pbar.update(1)

            pbar.set_description("Removing O6 where needed")
            get_ids_and_remove_o6(config)
            pbar.update(1)

        pbar.set_description("Filtering ligands")
        filter_ligands(res, rscc, rmsd, config)
        pbar.update(1)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--config", help="Path to config file", type=str, default="config.json")
    parser.add_argument("-t", "--test_mode", action="store_true",
                        help="Weather to run the whole process in a test mode")
    parser.add_argument("--min_rscc", help="Minimum RSCC used to define graph area",
                        type=float, default=0.85)
    parser.add_argument("--max_rscc", help="Maximum RSCC used to define graph area",
                        type=float, default=1.0)
    parser.add_argument("--min_rmsd", help="Minimum RMSD used to define graph area",
                        type=float, default=2.0)
    parser.add_argument("--max_rmsd", help="Maximum RMSD used to define graph area",
                        type=float, default=3.0)
    # FIXME: Get rid of graphs in process completely?
    parser.add_argument("--res", help="Value of maximum overall resolution of structure",
                        type=float, default=3.0)
    parser.add_argument("--rscc", help="Value of minimum RSCC of residue",
                        type=float, default=0.8)
    parser.add_argument("--rmsd", help="Value of maximum RMSD of residue",
                        type=float, default=2.0)
    parser.add_argument("-g", "--make_graphs", action="store_true",
                        help="Weather to plot and analyse graphs of residues")

    args = parser.parse_args()

    config = Config.load(args.config, None, False, args)

    setup_logger(config.log_path)

    is_unix = system() != "Windows"

    with logging_redirect_tqdm():
        main(config, is_unix, args.min_rscc, args.max_rscc, args.min_rmsd, args.max_rmsd,
             args.res, args.rscc, args.rmsd, args.make_graphs, args.test_mode)

        Config.clear_current_run()
