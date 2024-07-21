from csv import DictReader, DictWriter

import pandas as pd

from config import Config


def get_average_rmsd_of_peaks(config: Config) -> None:
    """
    Find average rmsd of peaks in the histograms

    :param config: Config object
    """
    df = pd.read_csv(config.validation_results /  "merged_rscc_rmsd.csv")
    data = df[df["name"] == "BGC"]
    filtered_df1 = data[data["rmsd"] <= 0.4]#FIXME: Extract to variables
    filtered_df2 = data[(data["rmsd"] > 0.4) & (data["rmsd"] < 0.7)]#FIXME: Extract to variables
    average1 = filtered_df1["rmsd"].mean()
    average2 = filtered_df2["rmsd"].mean()

    print(average1, average2, sep="\n")#FIXME: Print in main


def analyze_graph(min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float, config: Config) -> None:
    """
    Analyze which sugars are in the defined area of the graph

    :param min_rscc: Minimum RSCC used to define graph area
    :param max_rscc: Maximum RSCC used to define graph area
    :param min_rmsd: Minimum RMSD used to define graph area
    :param max_rmsd: Maximum RMSD used to define graph area
    :param config: Config object
    """
    #FIXME: Load merged_rscc_rmsd.csv to pandas, filter (delete data for which the if is not true), then save to graph_analysis file
    with open(config.results_folder / "graph_analysis" / f"graph_analysis_{min_rscc}_{max_rscc}_{min_rmsd}_{max_rmsd}.csv", "w", newline="") as f:
        writer = DictWriter(f, ["pdb", "resolution", "name", "num", "chain", "rscc", "type", "rmsd"])
        writer.writeheader()
        with open(config.validation_results /  "merged_rscc_rmsd.csv", "r") as f:
            rscc_rmsd = DictReader(f)
            sugars = set()
            for row in rscc_rmsd:
                if float(row["rmsd"]) >= min_rmsd and float(row["rmsd"]) <= max_rmsd and float(row["rscc"]) >= min_rscc and float(row["rscc"]) <= max_rscc:
                    sugars.add(row["name"])
                    #print(row)
                    writer.writerow(row)

    print(sugars)#FIXME: Print in main
    print(len(sugars))


def main(config: Config, min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float):

    get_average_rmsd_of_peaks(config)
    analyze_graph(min_rscc, max_rscc, min_rmsd, max_rmsd, config)


if __name__ == "__main__":
    #TODO: Add argparse (might not be needed if all in two main scripts)
    config = Config.load("config.json")

    (config.results_folder / "graph_analysis").mkdir(exist_ok=True, parents=True)

    main(config, 0.85, 1.0, 2.0, 3.0)
