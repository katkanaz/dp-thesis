from pathlib import Path

import pandas as pd

MERGED_CSV_PATH = Path("/Volumes/YangYang/diplomka/results/validation") / "merged_rscc_rmsd.csv"


def get_average_rmsd_of_peaks() -> None:
    #TODO: add docs
    """
    Find average rmsd of those two peaks appearing in the histograms.
    """
    df = pd.read_csv(MERGED_CSV_PATH)
    data = df[df["name"] == "BGC"]
    filtered_df1 = data[data["rmsd"] <= 0.4]
    filtered_df2 = data[(data["rmsd"] > 0.4) & (data["rmsd"] < 0.7)]
    average1 = filtered_df1["rmsd"].mean()
    average2 = filtered_df2["rmsd"].mean()

    print(average1, average2) #FIXME

if __name__ == "__main__":
    get_average_rmsd_of_peaks()