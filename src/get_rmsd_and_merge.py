import csv
import json
from pathlib import Path

import pandas as pd

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"


# after runnig MV, extracting RMSD from results
def get_rmsd_and_merge() -> None:
    #TODO: add docs
    """
    Gets RMSDs from MotiveValidator results and merges them with the file with resolutions and RSCC values.
    """
    with open(Path(__file__).parent.parent / f"mv_cmd_line/mv_results/result/result/result.json") as f:
        data = json.load(f)
    with open(RESULTS_FOLDER / "validation" / "all_rmsd.csv", "w", newline="") as f:
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

    rscc = pd.read_csv(RESULTS_FOLDER / "validation" / "all_rscc_and_resolution.csv")
    rmsd = pd.read_csv(RESULTS_FOLDER / "validation" / "all_rmsd.csv")

    merged = rscc.merge(rmsd, on=["pdb", "name", "num", "chain"])
    merged.to_csv(RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv", index=False)


if __name__ == "__main__":
    get_rmsd_and_merge()
