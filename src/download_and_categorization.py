"""
Script Name: download_and_categorization.py
Description: Download structures with sugars from PDB and perform sugar categorization.
Author: Kateřina Nazarčuková
"""

#TODO: import libs
from argparse import ArgumentParser
from pathlib import Path

from config import Config

from download_files import download_files
from categorize import categorize
from extract_rscc_and_resolution import extract_rscc_and_resolution
from run_mv import run_mv
from plot_graphs import plot_graphs
from graph_analysis import graph_analysis
from process_and_filter_ligands import process_and_filter_ligands

def main():

    # run_mv()

if __name__ == "__main__":
    config = Config.load("config.json")

    main()
