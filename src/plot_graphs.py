"""
Script Name: plot_graphs.py
Description: Plot different types of graphs for the sugar residues.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


import matplotlib.pyplot as plt
import pandas as pd
from logger import setup_logger

from configuration import Config


def plot_corr_graphs(config: Config):
    """
    Create correlation graphs of RSCC and RMSD for all residues and also separately just for ligands,
    glycosylated residues and residues in close contacts. Also create these graphs separately for each
    of the 10 most abundant sugar types among PDB structures

    :param config: Config objects
    :param graphs: Path to save the results
    """

    (config.residue_graphs_dir / "individual_sugars" / "correlation").mkdir(exist_ok=True, parents=True)
    data = pd.read_csv(config.validation_dir / "merged_rscc_rmsd.csv")

    residue_types  = ["all", "ligand", "glycosylated", "close"]
    most_abundant_residues = ["NAG", "MAN", "GLC", "BMA", "BGC", "GAL", "FUC", "SIA"]
    #most_abundant_residues = ["LMT", "BOG"]

    for residue_type in residue_types:
        if residue_type != "all":
            data.loc[data["type"] == residue_type].plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=residue_type, color="green")
            plt.xlim([0, 8])
            plt.ylim([-0.4, 1])
            plt.yticks(ticks=[-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], labels=["-0,4", "-0,2", "0,0", "0,2", "0,4", "0,6", "0,8", "1,0"])
            plt.tick_params(labelsize="medium")
            plt.xlabel("RMSD")
            plt.ylabel("RSCC")
            plt.savefig(config.residue_graphs_dir / f"all_{residue_type}.svg")
            plt.close()

        else:
            data.plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=f"Korelace RMSD a RSCC pro všechny cukry", color="green")
            plt.xlim([0, 8])
            plt.ylim([-0.4, 1])
            plt.yticks(ticks=[-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], labels=["-0,4", "-0,2", "0,0", "0,2", "0,4", "0,6", "0,8", "1,0"])
            plt.tick_params(labelsize="medium")
            plt.xlabel("RMSD")
            plt.ylabel("RSCC")
            plt.savefig(config.residue_graphs_dir / "all.svg")
            plt.close()

    for res in most_abundant_residues:
        data.loc[(data["name"] == res)].plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=res, color="green")
        plt.xlim([0, 3])
        plt.xticks(ticks=[0, 1, 2, 3])
        plt.ylim([-0.5, 1])
        plt.yticks(ticks=[-0.5, 0, 0.5, 1], labels=["-0,5", "0", "0,5", None])
        plt.tick_params(labelsize="medium")
        plt.xlabel("RMSD", size="medium")
        plt.ylabel("RSCC", size="medium")
        plt.savefig(config.residue_graphs_dir / "individual_sugars" / "correlation" / f"{res}.svg")
        plt.close()


def plot_histograms(config: Config):
    """
    Make histograms for individual sugars

    :param config: Config objects
    :param graphs: Path to save the results
    """

    (config.residue_graphs_dir / "individual_sugars" / "histograms").mkdir(exist_ok=True)
    data = pd.read_csv(config.validation_dir / "merged_rscc_rmsd.csv")
    new_data = data.filter(items=["rmsd"])

    most_abundant_residues = ["NAG", "MAN", "GLC", "BMA", "BGC", "GAL", "FUC", "SIA"]
    #most_abundant_residues = ["LMT", "BOG"]
    for sugar in most_abundant_residues:
        new_data.loc[(data["name"] == sugar)].plot(kind="hist", bins=30, grid=False, title=sugar, fontsize="45", color="green")
        plt.xlim([0, 3])
        plt.xlabel("RMSD", size="medium")
        plt.ylabel("Frequency", size="medium")
        plt.xticks(ticks=[0, 1, 2, 3])

        plt.tick_params(labelsize="medium")

        plt.legend().remove()
        plt.savefig(config.residue_graphs_dir / "individual_sugars" / "histograms" / f"{sugar}.svg")
        plt.close()


def plot_3D_graph(config: Config):
    # FIXME: Add docstring
    """
    [TODO:description]

    :param config: Config objects
    :param graphs: Path to save the results
    """

    data = pd.read_csv(config.validation_dir / "merged_rscc_rmsd.csv")
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel("RMSD")
    ax.set_ylabel("Resolution")
    ax.set_zlabel("RSCC")
    ax.scatter(data["rmsd"], data["resolution"], data["rscc"], linewidths=0.5, marker=".", color="green")
    plt.savefig(config.residue_graphs_dir / f"3D_graph.svg")
    plt.close()


def plot_graphs(config: Config):
    # Tmp # FIXME:
    (config.residue_graphs_dir).mkdir(exist_ok=True, parents=True)

    plot_corr_graphs(config)
    plot_histograms(config)
    plot_3D_graph(config)


if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    # (config.residue_graphs_dir).mkdir(exist_ok=True, parents=True)

    plot_graphs(config)
