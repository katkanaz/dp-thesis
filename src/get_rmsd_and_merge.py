import csv
import json

import pandas as pd

from config import Config


# After runnig MV, extract RMSD from results
def get_rmsd_and_merge(config: Config) -> None:
    """
    Get RMSDs from MotiveValidator results and merge them with the values of resolution and RSCC

    :param config: Config object
    """

    with open(config.mv_results / f"result/result/result.json") as f:
        data = json.load(f)
    with open(config.validation_results / "all_rmsd.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pdb", "name", "num", "chain", "rmsd"])
        for model in data["Models"]:
            for entry in model["Entries"]:
                pdb = entry["Id"].split("_")[0]
                res = str(entry["MainResidue"]).split()
                try:
                    row = [pdb.upper(), res[0], res[1], res[2], str(entry["ModelRmsd"])]
                except:
                    continue
                writer.writerow(row)

    rscc = pd.read_csv(config.results_folder / "validation" / "all_rscc_and_resolution.csv")
    rmsd = pd.read_csv(config.results_folder / "validation" / "all_rmsd.csv")

    merged = rscc.merge(rmsd, on=["pdb", "name", "num", "chain"])
    merged.to_csv(config.validation_results / "merged_rscc_rmsd.csv", index=False)


if __name__ == "__main__":
    config = Config.load("config.json")

    get_rmsd_and_merge(config)
