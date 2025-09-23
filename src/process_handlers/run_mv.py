"""
Script Name: run_mv.py
Description: Modify model file, download and run MotiveValidator and extract results.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


import csv
import json
from platform import system
from subprocess import Popen, PIPE
from zipfile import ZipFile

import gemmi
import pandas as pd
import requests
from logger import logger, setup_logger

from configuration import Config
from utils.unzip_file import unzip_all


def remove_nonsugar_residues(config: Config) -> None:
    """
    Remove all the non-sugar residues from the model mmCIF file.

    :param config: Config object
    """

    logger.info("Creating model file")

    doc = gemmi.cif.read(str(config.components_dir / "components.cif.gz"))
    for i in range(len(doc) - 1, -1, -1):
        comp_type = doc[i].find_value('_chem_comp.type')
        if "saccharide" not in comp_type.lower():
            del doc[i]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20
    doc.write_file(str(config.components_dir / "components_sugars_only.cif"), options)


def download_mv(config: Config) -> None:
    """
    Download latest version of MotiveValidator and extract the contents of a zip file.

    :param config: Config object
    """

    logger.info("Downloading MotiveValidator")

    response = requests.get("https://webchem.ncbr.muni.cz/Platform/MotiveValidator/DownloadService")
    with open((config.user_cfg.mv_dir / "MotiveValidator.zip"), "wb") as f: # FIXME: Keep version number
        f.write(response.content)

    unzip_all(config.user_cfg.mv_dir / "MotiveValidator.zip", config.user_cfg.mv_dir / "MotiveValidator")


# TODO: finish function
# def update_mv(config: Config):
    # download change log and read current version in it
    # if version same delete changelog and do nothing else
    # if not download again current mv and delete changelow


def create_mv_config(config: Config) -> None:
    """
    Create MotiveValidator config file.

    :param config: Config object
    """

    logger.info("Creating config file")

    mv_config = {
        "ValidationType": "Sugars",
        "InputFolder":  str(config.modified_mmcif_files_dir),
        "ModelsSource": str(config.components_dir / "components_sugars_only.cif"),
        "IsModelsSourceComponentDictionary": True,
        "IgnoreObsoleteComponentDictionaryEntries": False,
        "SummaryOnly": False,
        "DatabaseModeMinModelAtomCount": 0,
        "DatabaseModeIgnoreNames": [],
        "MaxDegreeOfParallelism": 8
    }

    with open(config.mv_run_dir / "mv_config.json", "w", encoding="utf8") as f:
        json.dump(mv_config, f, indent=4)


def get_rmsd_and_merge(config: Config) -> None:
    """
    Get RMSDs from MotiveValidator results and merge them with the values of resolution and RSCC.

    :param config: Config object
    """

    logger.info("Extracting results")

    with ZipFile(config.mv_run_dir / "results/result/result.zip", "r") as zip_ref:
        zip_ref.extractall(config.mv_run_dir / "results/result/result")

    with open(config.mv_run_dir / "results/result/result/result.json", encoding="utf8") as f:
        data = json.load(f)
    with open(config.validation_dir / "all_rmsd.csv", "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(["pdb", "name", "num", "chain", "rmsd"])
        for model in data["Models"]:
            for entry in model["Entries"]:
                pdb = entry["Id"].split("_")[1]
                res = str(entry["MainResidue"]).split()
                try:
                    row = [pdb.upper(), res[0], res[1], res[2], str(entry["ModelRmsd"])]
                except:
                    continue
                writer.writerow(row)

    rscc = pd.read_csv(config.validation_dir / "all_rscc_and_resolution.csv") # FIXME: will it have different pdb ids????
    rmsd = pd.read_csv(config.validation_dir / "all_rmsd.csv")

    merged = rscc.merge(rmsd, on=["pdb", "name", "num", "chain"])
    merged.to_csv(config.validation_dir / "merged_rscc_rmsd.csv", index=False)


def run_mv(config: Config, is_unix: bool) -> None:
    # Tmp # FIXME:
    (config.mv_run_dir / "results").mkdir(exist_ok=True, parents=True)
    (config.user_cfg.mv_dir).mkdir(exist_ok=True, parents=True)

    # Prerequisits for running MV
    remove_nonsugar_residues(config)
    dir_path = config.user_cfg.mv_dir / "MotiveValidator"
    if not dir_path.exists() or (dir_path.is_dir() and not any(dir_path.iterdir())):
        download_mv(config)
    # update_mv(config) # TODO: If just downloaded do not update
    create_mv_config(config)

    cmd = [f"{'mono ' if is_unix is True else ''}"
           f"{config.user_cfg.mv_dir}/MotiveValidator/WebChemistry.MotiveValidator.Service.exe "
           f"{config.mv_run_dir}/results "
           f"{config.mv_run_dir}/mv_config.json"]

    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as mv_proc:
        assert mv_proc.stdout is not None, "stdout is set to PIPE in Popen"
        for line in mv_proc.stdout:
            logger.info(f"STDOUT: {line.strip()}")
        assert mv_proc.stderr is not None, "stderr is set to PIPE in Popen"
        for line in mv_proc.stderr:
            logger.error(f"STDERR: {line.strip()}")

    if mv_proc.returncode != 0:
        logger.error(f"MV process exited with code {mv_proc.returncode}")
    else:
        logger.info("MV process completed successfully")

    # Extract results
    get_rmsd_and_merge(config)


if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    is_unix = system() != "Windows"

    run_mv(config, is_unix)
