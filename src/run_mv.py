"""
Script Name: run_mv.py
Description: Modify model file, download and run MotiveValidator and extract results.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""

import csv
import json
from platform import system
import requests
import subprocess
from zipfile import ZipFile

import gemmi
import pandas as pd

from config import Config


def remove_nonsugar_residues(config: Config) -> None:
    """
    Remove all the non-sugar residues from the model mmCIF file

    :param config: Config object
    """

    print("Creating model file")

    doc = gemmi.cif.read(str(config.data_folder / "components.cif.gz"))
    for i in range(len(doc) - 1, -1, -1): 
        comp_type = doc[i].find_value('_chem_comp.type')
        if "saccharide" not in comp_type.lower(): 
            del doc[i]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20
    doc.write_file(str(config.mv_folder / "model_source" / "components_sugars_only.cif"), options)


def download_mv(config: Config) -> None:
    """
    Download latest version of MotiveValidator and extract the contents of a zip file

    :param config: Config object
    """

    print("Downloading MotiveValidator")

    response = requests.get(f"https://webchem.ncbr.muni.cz/Platform/MotiveValidator/DownloadService")
    with open((config.mv_folder / "MotiveValidator.zip"), "wb") as f:
        f.write(response.content)

    with ZipFile(config.mv_folder / "MotiveValidator.zip", "r") as zip_ref:
        zip_ref.extractall(config.mv_folder / "MotiveValidator")


# def update_mv(config: Config):#TODO: finish function
    # download change log and read current version in it
    # if version same delete changelog and do nothing else
    # if not download again current mv and delete changelow


def create_mv_config(config: Config) -> None:
    """
    Create MotiveValidator config file

    :param config: Config object
    """

    print("Creating config file")

    mv_config = {
        "ValidationType": "Sugars",
        "InputFolder": f"{config.data_folder}/mmcif_files",
        "ModelsSource": f"{config.mv_folder}/model_source/components_sugars_only.cif",
        "IsModelsSourceComponentDictionary": True,
        "IgnoreObsoleteComponentDictionaryEntries": False,
        "SummaryOnly": False,
        "DatabaseModeMinModelAtomCount": 0,
        "DatabaseModeIgnoreNames": [],
        "MaxDegreeOfParallelism": 8
    }

    with open(config.mv_folder / "mv_config.json", "w") as f:
        json.dump(mv_config, f, indent=4)


def get_rmsd_and_merge(config: Config) -> None:
    """
    Get RMSDs from MotiveValidator results and merge them with the values of resolution and RSCC

    :param config: Config object
    """

    print("Extracting results")

    with ZipFile(config.mv_folder / "results/result/result.zip", "r") as zip_ref:
        zip_ref.extractall(config.mv_folder / "results/result/result")

    with open(config.mv_folder / "results/result/result/result.json") as f:
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


def run_mv(config: Config, is_unix: bool):
    # Prerequisits for running MV
    remove_nonsugar_residues(config)
    dir_path = config.mv_folder / "MotiveValidator"
    if not dir_path.exists() or (dir_path.is_dir() and not any(dir_path.iterdir())):
        download_mv(config)
    # update_mv(config) #TODO: if just downloaded do not update
    create_mv_config(config)

    cmd = [f"{'mono ' if is_unix is True else ''}"
           f"{config.mv_folder}/MotiveValidator/WebChemistry.MotiveValidator.Service.exe "
           f"{config.mv_folder}/results "
           f"{config.mv_folder}/mv_config.json"]
    subprocess.run(cmd, shell=True)#TODO: log output

    # Extract results
    get_rmsd_and_merge(config)


if __name__ == "__main__":
    config = Config.load("config.json")
    (config.mv_folder / "model_source").mkdir(exist_ok=True, parents=True)
    (config.mv_folder / "results").mkdir(exist_ok=True, parents=True)

    is_unix = system() != "Windows"

    run_mv(config, is_unix)
