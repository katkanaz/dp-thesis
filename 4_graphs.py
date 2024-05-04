from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
DATA_FOLDER = Path("/Volumes/YangYang/diplomka") / "data"

data_path = RESULTS_FOLDER / "validation" / "merged_rscc_rmsd.csv"
results_path = RESULTS_FOLDER / "graphs"
results_path.mkdir(exist_ok=True, parents=True)


def make_corr_graphs():
    #TODO: add docs
    """
    Creates correlation graphs of RSCC and RMSD for all residues and also separately just for ligands,
    glycosylated residues and residues in close contacts. Also cretates these graphs separately for each
    of the 10 most abundant sugar types among pdb structures.
    """
    (results_path / "individual_sugars" / "correlation").mkdir(exist_ok=True, parents=True)
    data = pd.read_csv(data_path)

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
            plt.savefig(results_path / f"all_{residue_type}")
            plt.close()

        else:
            data.plot(kind="scatter", x="rmsd", y="rscc", marker=".", linewidth=0.2, title=f"Korelace RMSD a RSCC pro všechny cukry", color="green")
            plt.xlim([0, 8])
            plt.ylim([-0.4, 1])
            plt.yticks(ticks=[-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1], labels=["-0,4", "-0,2", "0,0", "0,2", "0,4", "0,6", "0,8", "1,0"])
            plt.tick_params(labelsize="medium")
            plt.xlabel("RMSD")
            plt.ylabel("RSCC")
            plt.savefig(results_path / f"all")
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
        plt.savefig(results_path / "individual_sugars" / "correlation" / res)
        plt.close()


def make_histograms():
    #TODO: add docs
    (results_path / "individual_sugars" / "histograms").mkdir(exist_ok=True)
    data = pd.read_csv(data_path)
    new_data = data.filter(items=["rmsd"])

    most_abundant_residues = ["NAG", "MAN", "GLC", "BMA", "BGC", "GAL", "FUC", "SIA"]
    #most_abundant_residues = ["LMT", "BOG"]
    for sugar in most_abundant_residues:
        new_data.loc[(data["name"] == sugar)].plot(kind="hist", bins=30, grid=False, title=sugar, fontsize="45", color="green")
        plt.xlim([0, 3])
        plt.xlabel("RMSD", size="medium")
        plt.ylabel("Frekvence", size="medium")
        plt.xticks(ticks=[0, 1, 2, 3])

        plt.tick_params(labelsize="medium")

        plt.legend().remove()
        #plt.show()
        plt.savefig(results_path / "individual_sugars" / "histograms" / sugar)
        plt.close()


def make_3D_graph():
    #TODO: add docs
    data = pd.read_csv(data_path)
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel("RMSD")
    ax.set_ylabel("Resolution")
    ax.set_zlabel("RSCC")
    ax.scatter(data["rmsd"], data["resolution"], data["rscc"], linewidths=0.5, marker=".", color="green")
    #plt.show()
    plt.savefig(results_path / f"3D_graph")
    plt.close()


def main():
    make_corr_graphs()
    make_histograms()
    make_3D_graph()


if __name__ == "__main__":
    main()
