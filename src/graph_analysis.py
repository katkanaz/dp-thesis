"""
Script Name: graph_analysis.py
Description: Perform different kinds of analysis of obtained graphs.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
from csv import DictReader, DictWriter

import pandas as pd
from logger import logger, setup_logger

from configuration import Config


def get_average_rmsd_of_peaks(config: Config) -> None:
    """
    Find average rmsd of peaks in the histograms

    :param config: Config object
    """
    df = pd.read_csv(config.validation_dir /  "merged_rscc_rmsd.csv")
    data = df[df["name"] == "BGC"]
    filtered_df1 = data[data["rmsd"] <= 0.4] # FIXME: Extract to variables
    filtered_df2 = data[(data["rmsd"] > 0.4) & (data["rmsd"] < 0.7)] # FIXME: Extract to variables
    average1 = filtered_df1["rmsd"].mean()
    average2 = filtered_df2["rmsd"].mean()

    logger.info(f"Average RMSD of peaks for RMSD <= 0.4: {average1}")
    logger.info(f"Average RMSD of peaks for RMSD > 0.4 and < 0.7: {average2}")


def analyze_graph(min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float, config: Config) -> None:
    """
    Analyze which sugars are in the defined area of the graph

    :param min_rscc: Minimum RSCC used to define graph area
    :param max_rscc: Maximum RSCC used to define graph area
    :param min_rmsd: Minimum RMSD used to define graph area
    :param max_rmsd: Maximum RMSD used to define graph area
    :param config: Config object
    """
    # FIXME: Load merged_rscc_rmsd.csv to pandas, filter (delete data for which the if is not true), then save to graph_analysis file
    with open(config.graph_analysis_dir / f"graph_analysis_{min_rscc}_{max_rscc}_{min_rmsd}_{max_rmsd}.csv", "w", newline="") as f:
        writer = DictWriter(f, ["pdb", "resolution", "name", "num", "chain", "rscc", "type", "rmsd"])
        writer.writeheader()
        with open(config.validation_dir /  "merged_rscc_rmsd.csv", "r") as f:
            rscc_rmsd = DictReader(f)
            sugars = set()
            for row in rscc_rmsd:
                if float(row["rmsd"]) >= min_rmsd and float(row["rmsd"]) <= max_rmsd and float(row["rscc"]) >= min_rscc and float(row["rscc"]) <= max_rscc:
                    sugars.add(row["name"])
                    #print(row)
                    writer.writerow(row)

    logger.info(f"Number of sugars in the defined area of the graph {len(sugars)}")
    logger.info(f"Types of sugars in the defined area of the graph: {sugars}")


def graph_analysis(config: Config, min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float):
    get_average_rmsd_of_peaks(config)
    analyze_graph(min_rscc, max_rscc, min_rmsd, max_rmsd, config)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--min_rscc", help="Minimum RSCC used to define graph area",
                        type="float", default=0.85)
    parser.add_argument("--max_rscc", help="Maximum RSCC used to define graph area",
                        type="float", default=1.0)
    parser.add_argument("--min_rmsd", help="Minimum RMSD used to define graph area",
                        type="float", default=2.0)
    parser.add_argument("--max_rmsd", help="Maximum RMSD used to define graph area",
                        type="float", default=3.0)

    args = parser.parse_args()

    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    config.graph_analysis_dir.mkdir(exist_ok=True, parents=True)

    graph_analysis(config, args.min_rscc, args.max_rscc, args.min_rmsd, args.max_rmsd)
