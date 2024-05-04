from csv import DictReader, DictWriter
from pathlib import Path

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
SAVE_ANALYSIS = RESULTS_FOLDER / "graph_analysis"
SAVE_ANALYSIS.mkdir(exist_ok=True, parents=True)


def analyze_graph(min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float, name=None) -> None:
    #TODO: what is the name argument?
    #TODO: add docs
    """
    Prints what kind of sugars are in the defined area on the graph.
    """
    with open(SAVE_ANALYSIS / f"graph_analysis_{min_rscc}_{max_rscc}_{min_rmsd}_{max_rmsd}.csv", "w", newline="") as f:
        writer = DictWriter(f, ["pdb", "resolution", "name", "num", "chain", "rscc", "type", "rmsd"])
        writer.writeheader()
        with open(RESULTS_FOLDER / "validation" /  "merged_rscc_rmsd.csv") as f:
            rscc_rmsd = DictReader(f)
            sugars = set()
            for row in rscc_rmsd:
                if float(row["rmsd"]) >= min_rmsd and float(row["rmsd"]) <= max_rmsd and float(row["rscc"]) >= min_rscc and float(row["rscc"]) <= max_rscc:
                    sugars.add(row["name"])
                    #print(row)
                    writer.writerow(row)

    print(sugars)
    print(len(sugars))


if __name__ == "__main__":
    #TODO: add argparse
    analyze_graph(0.85, 1.0, 2.0, 3.0, name=None)