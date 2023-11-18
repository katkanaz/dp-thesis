from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULTS_FOLDER = Path(__file__).parent.parent / "results"
DATA_FOLDER = Path(__file__).parent.parent / "data"

data_path = RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv"
results_path = RESULTS_FOLDER / "graphs"
results_path.mkdir(exist_ok=True, parents=True)


def make_corr_graphs():
    """
    Creates correlation graphs of RSCC and RMSD for all residues and also separately just for ligands,
    glycosylated residues and residues in close contacts. Also cretates these graphs separately for each
    of the 10 most abundant sugar types among pdb structures.
    """
    (results_path / "jednotlive cukry" / "correlation").mkdir(exist_ok=True, parents=True)
    data = pd.read_csv(data_path / "merged_rscc_rmsd.csv")

    residue_types  = ["all", "ligand", "glycosylated", "close"]
    most_abundant_residues = ["NAG", "MAN", "GLC", "BMA", "BGC", "GAL", "FUC", "SIA"]
    #most_abundant_residues = ["LMT", "BOG"]

    for residue_type in residue_types:
        if residue_type != "all":
            data.loc[data["type"] == residue_type].plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=residue_type)
            plt.xlim([0, 8])
            plt.ylim([-0.4, 1])
            plt.yticks(ticks=[-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], labels=["-0,4", "-0,2", "0,0", "0,2", "0,4", "0,6", "0,8", "1,0"])
            plt.tick_params(labelsize="medium")
            plt.xlabel("RMSD")
            plt.ylabel("RSCC")
            plt.savefig(results_path / f"all_{residue_type}")
            plt.close()

        else:
            data.plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=f"Korelácia RMSD a RSCC pre všetky cukry")
            plt.xlim([0, 8])
            plt.ylim([-0.4, 1])
            plt.yticks(ticks=[-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], labels=["-0,4", "-0,2", "0,0", "0,2", "0,4", "0,6", "0,8", "1,0"])
            plt.tick_params(labelsize="medium")
            plt.xlabel("RMSD")
            plt.ylabel("RSCC")
            plt.savefig(results_path / f"all")
            plt.close()

    for res in most_abundant_residues:
        data.loc[(data["name"] == res)].plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=res)
        plt.xlim([0, 3])
        plt.xticks(ticks=[0, 1, 2, 3])
        plt.ylim([-0.5, 1])
        plt.yticks(ticks=[-0.5, 0, 0.5, 1], labels=["-0,5", "0", "0,5", None])
        plt.tick_params(labelsize="xx-large")
        plt.xlabel("RMSD", size="xx-large")
        plt.ylabel("RSCC", size="xx-large")
        plt.savefig(results_path / "jednotlive cukry" / "correlation" / res)
        plt.close()


def make_histograms():
    (results_path / "jednotlive cukry" / "histograms").mkdir(exist_ok=True)
    data = pd.read_csv(data_path / "merged_rscc_rmsd.csv")
    new_data = data.filter(items=["rmsd"])

    most_abundant_residues = ["NAG", "MAN", "GLC", "BMA", "BGC", "GAL", "FUC", "SIA"]
    #most_abundant_residues = ["LMT", "BOG"]
    for sugar in most_abundant_residues:
        new_data.loc[(data["name"] == sugar)].plot(kind="hist", bins=30, grid=False, title=sugar, fontsize="50")
        plt.xlim([0, 3])
        plt.xlabel("RMSD", size="xx-large")
        plt.ylabel("Frekvencia", size="xx-large")
        plt.xticks(ticks=[0, 1, 2, 3])

        plt.tick_params(labelsize="xx-large")

        plt.legend().remove()
        #plt.show()
        plt.savefig(results_path / "jednotlive cukry" / "histograms" / sugar)
        plt.close()


def make_3D_graph():
    data = pd.read_csv(data_path / "merged_rscc_rmsd.csv")
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel("rmsd")
    ax.set_ylabel("resolution")
    ax.set_zlabel("rscc")
    ax.scatter(data["rmsd"], data["resolution"], data["rscc"], linewidths=0.5, marker=".")
    plt.show()
    plt.savefig(results_path / f"3D_graph")
    plt.close()


def main():
    make_corr_graphs()
    make_histograms()


if __name__ == "__main__":
    main()
