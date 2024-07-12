#TODO: Create one graph_analysis script
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

    print(average1, average2)

if __name__ == "__main__":
    #TODO: Add argparse

    config = Config.load("config.json")

    get_average_rmsd_of_peaks(config)
