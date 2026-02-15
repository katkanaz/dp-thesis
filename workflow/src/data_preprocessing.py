"""
Script Name: download_and_categorization.py
Description: Download structures with sugars from PDB,
             get all residues that are ligands and filter them. 
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from datetime import datetime
from platform import system

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from logger import logger, setup_logger

from configuration import Config

from process_handlers.download_files import download_files
from process_handlers.categorize import categorize
from process_handlers.alternative_conformations import create_separate_mmcifs
# from process_handlers.alternative_conformations import mock_altloc_separation
from process_handlers.extract_rscc_and_resolution import extract_rscc_and_resolution
from process_handlers.run_mv import run_mv
from process_handlers.filter_ligands import filter_ligands


def main(config: Config, is_unix: bool, res: float, rscc: float, rmsd: float, test_mode: bool) -> None:

    with tqdm(total=6) as pbar: 
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

        pbar.set_description("Filtering ligands")
        filter_ligands(res, rscc, rmsd, config)
        pbar.update(1)


if __name__ == "__main__":
    start_time = datetime.now()

    parser = ArgumentParser()

    parser.add_argument("--config", help="Path to config file", type=str, default="config.json")
    parser.add_argument("-t", "--test_mode", action="store_true",
                        help="Weather to run the whole process in a test mode")
    parser.add_argument("--res", help="Value of maximum overall resolution of structure",
                        type=float, default=3.0)
    parser.add_argument("--rscc", help="Value of minimum RSCC of residue",
                        type=float, default=0.8)
    parser.add_argument("--rmsd", help="Value of maximum RMSD of residue",
                        type=float, default=2.0)
    parser.add_argument("--keep_current_run", help="Don't end the current run (won't delete .current_run file)", action="store_true")

    args = parser.parse_args()

    config = Config.load(args.config, None, False, args)

    setup_logger(config.log_path)
    logger.info(f"Called with the following arguments: {vars(args)}")

    is_unix = system() != "Windows"

    with logging_redirect_tqdm():
        main(config, is_unix, args.res, args.rscc, args.rmsd, args.test_mode)

        if not args.keep_current_run:
            Config.clear_current_run()

    end_time = datetime.now()
    duration = end_time - start_time
    seconds = duration.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    logger.info(f"Program completed successfully in {int(hours)}h {int(minutes)}m {int(seconds)}s")
