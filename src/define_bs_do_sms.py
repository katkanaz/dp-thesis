"""
Script Name: define_bs_do_sms.py
Description: Define representative binding sites for a given sugar using PQ and PyMOL,
cluster obtained data and choose representatives to perform structure motif search with.
Author: Kateřina Nazarčuková
"""
#TODO: import libs
from argparse import ArgumentParser
from pathlib import Path

from config import Config

from run_pq import run_pq
from perform_alignment import perform_alignment
from cluster_data import cluster_data
from compare_clusters import compare_clusters
from create_tanglegram import create_tanglegram

def main():


if __name__ == "__main__":
    config = Config.load("config.json")

    main()



