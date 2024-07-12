#TODO: Create one graph_analysis script
from csv import DictReader, DictWriter
from pathlib import Path

from config import Config


def analyze_graph(min_rscc: float, max_rscc: float, min_rmsd: float, max_rmsd: float, config: Config, analysis_result: Path) -> None:
    """
    Analyze which sugars are in the defined area of the graph

    :param min_rscc: Minimum RSCC used to define graph area
    :param max_rscc: Maximum RSCC used to define graph area
    :param min_rmsd: Minimum RMSD used to define graph area
    :param max_rmsd: Maximum RMSD used to define graph area
    :param config: Config object
    :param analysis_result: Path to save results
    """
    #FIXME: Load merged_rscc_rmsd.csv to pandas, filter (delete data for which the if is not true), then save to graph_analysis file
    with open(analysis_result / f"graph_analysis_{min_rscc}_{max_rscc}_{min_rmsd}_{max_rmsd}.csv", "w", newline="") as f:
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

    print(sugars)
    print(len(sugars))


if __name__ == "__main__":
    #TODO: Add argparse (might not be needed if all in two main scripts)
    config = Config.load("config.json")

    graph_analysis = config.results_folder / "graph_analysis"
    graph_analysis.mkdir(exist_ok=True, parents=True)

    analyze_graph(0.85, 1.0, 2.0, 3.0, config, graph_analysis)
