"""
Script Name: run_pq.py
Description: Download and run PatternQuery, then extract the results.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
from typing import List, Dict
import os
from pathlib import Path
from platform import system
import shutil
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory
import zipfile

import requests
from logger import logger, setup_logger

from configuration import Config


more_than_one_pattern = []          # just to check no more than one pattern for specific ResidueID was found
pq_couldnt_find_pattern = []        # some ResidueID couldn't be found by PQ because they have different ResidueID somehow 
result_folder_not_created = []      # just in case something else goes wrong
# FIXME: Fix the pq_results folder coming from first pq

def download_pq(config: Config) -> None:
    """
    Download latest version of PatternQuery and extract the contents of a zip file

    :param config: Config object
    """

    logger.info("Downloading PatternQuery")

    response = requests.get(f"https://webchem.ncbr.muni.cz/Platform/PatternQuery/DownloadService")
    with open((config.user_cfg.pq_dir / "PatternQuery.zip"), "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(config.user_cfg.pq_dir / "PatternQuery.zip", "r") as zip_ref:
        zip_ref.extractall(config.user_cfg.pq_dir / "PatternQuery")


# def update_mv(config: Config) -> None: # TODO: finish function
    # download change log and read current version in it
    # if version same delete changelog and do nothing else
    # if not download again current mv and delete changelow


def create_pq_config(config: Config, structure: str, residues: List[Dict[str, str]], sugar: str) -> List[str]:
    # FIXME: Reword docstring, residues type and description
    """
    Create config file for the given structure

    Every stucture can contain 0 - n residues of interest specified by <sugar>.
    If the current structure does not contain any rezidue of sugar of interest, empty list is returned - so the program can jump to the next structure.
    If at least one residue of interest is present:
    For every residue a separate query is needed. Therefore one config file with 1-n queries is created per structure.
    Then it is saved and a list of all query names is returnd.
    Name is in a form <pdb>_<name>_<num>_<chain>_*<case_sensitive_tag>*.pdb

    :param structure: PDB ID of structure
    :param residues [TODO:type]: [TODO:description]
    :param sugar: The sugar for which the representative binding site is being defined
    :return: List of query IDs
    """
    
    pq_config = {
        "InputFolders": [
            str(config.pq_run_dir / "structures"),
        ],
        "Queries": [],
        "StatisticsOnly": False,
        "MaxParallelism": 2
    }
    query_names = []

    # TODO: Reword
    # PQ queries are not case sensitive but there are structures which contain
    # two chains with the same letter but one upper and the other lower.
    # In that case eg. residues "GLC 1 M" and "GLC 1 m" would have the same
    # query in PQ sense. Therefore, tag "_2" is added to such queries.
    case_sensitive_check = []
    for residue in residues:
        if residue["name"] == sugar:
            case = f"{residue['num']}_{residue['chain']}"
            if case.upper() in case_sensitive_check or case.lower() in case_sensitive_check:
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}_2"
            else:
                case_sensitive_check.append(case)
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}"
            query_names.append(query_id)
            query_str = f"ResidueIds('{residue['num']} {residue['chain']}').AmbientResidues(5)"
            pq_config["Queries"].append({"Id": query_id, "QueryString": query_str})

    if query_names:
        # Create respective config file for current structure, with queries for every ligand of sugar of interest in that structure
        with open(config.pq_run_dir / "pq_config.json", "w") as f:
            json.dump(pq_config, f, indent=4)

    return query_names


def extract_results(target: Path, zip_result_folder: Path, query_names: List[str]) -> None:
    # FIXME: Reword
    """
    Unzip the results and rename and move each sugar surrounding (pattern) to one common folder

    Results are present in the zip folder, where every query has its own subfolder
    with the name same as was its query name: <pdb>_<name>_<num>_<chain>_*<key_sensitive_tag>*.pdb
    Each query is expected to have only one pattern found

    :param target: Common folder to move resulting binding sites to
    :param zip_result_folder: Path to zip folder containing PQ results
    :param query_names: List of query IDs
    """

    logger.info("Extractiong results")

    with TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_result_folder, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            for query_name in query_names: 
                results_path = Path(temp_dir) / query_name / "patterns"
                if not results_path.exists():
                    pq_couldnt_find_pattern.append(query_name)
                    continue
                # It is expected to have only one pattern found for one query, but checking just in case
                # TODO: add error flag
                if len(os.listdir(results_path)) > 1:
                    #global END_FLAG
                    #END_FLAG = True
                    #return
                    more_than_one_pattern.append(query_name)
                    continue
                for file in results_path.iterdir():
                    Path(file).rename(results_path / f"{query_name}.pdb")  # Rename the pattern so it is distinguishable
                src = results_path / f"{query_name}.pdb"
                shutil.move(str(src), str(target))


def run_pq(sugar: str, config: Config, is_unix: bool) -> None:
    (config.user_cfg.pq_dir).mkdir(exist_ok=True, parents=True)
    dir_path = config.user_cfg.pq_dir / "PatternQuery"
    if not dir_path.exists() or (dir_path.is_dir() and not any(dir_path.iterdir())):
        download_pq(config)
    # Tmp # FIXME:
    (config.pq_run_dir / "structures").mkdir(exist_ok=True, parents=True)
    (config.pq_run_dir / "results").mkdir(exist_ok=True, parents=True)


    with open(config.categorization_dir / "filtered_ligands.json", "r") as f:
        ligands: dict = json.load(f)

    target_dir = config.raw_binding_sites_dir
    target_dir.mkdir(exist_ok=True, parents=True)

    logger.info("Creating PatternQuerry configs")

    for structure, residues in ligands.items():
        structure = structure.lower()
        query_names = create_pq_config(config, structure, residues, sugar)
        if not query_names:
            continue
        # Copy current structure to ./structures dir which is used as source by PQ.
        src = config.mmcif_files_dir / f"{structure}.cif" #TODO: From modified mmcif
        dst = config.pq_run_dir / "structures" / f"{structure}.cif"
        shutil.copyfile(src, dst)

        # TODO: Extract to function

        # Run PQ
        cmd = [f"{'mono ' if is_unix is True else ''}"
               f"{config.user_cfg.pq_dir}/PatternQuery/WebChemistry.Queries.Service.exe "
               f"{config.pq_run_dir}/results "
               f"{config.pq_run_dir}/pq_config.json"]


        with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as pq_proc:
            assert pq_proc.stdout is not None, "stdout is set to PIPE in Popen" 
            for line in pq_proc.stdout:
                logger.info(f"STDOUT: {line.strip()}")
            assert pq_proc.stderr is not None, "stderr is set to PIPE in Popen" 
            for line in pq_proc.stderr:
                logger.error(f"STDERR: {line.strip()}")

        if pq_proc.returncode != 0:
            logger.error(f"PQ process exited with code {pq_proc.returncode}")
        else:
            logger.info("PQ process completed successfully")

        zip_result_folder = config.pq_run_dir / "results" / "result/result.zip"
        if not zip_result_folder.exists():
            result_folder_not_created.append(structure)
            # Delete the current structure from ./structures directory and continue to the next structure
            Path(config.pq_run_dir / "structures" / f"{structure}.cif").unlink()
            continue

        extract_results(target_dir, zip_result_folder, query_names)

        #if END_FLAG:
            #break

        # Delete the result folder and also the current structure from ./structures so the new one can be copied there
        (config.pq_run_dir / "structures" / f"{structure}.cif").unlink()
        shutil.rmtree(config.pq_run_dir / "results" / "result")

    logger.error(f"More patterns for one id found: {more_than_one_pattern}")
    logger.error(f"PQ could not find these patterns: {pq_couldnt_find_pattern}")
    logger.error(f"Result folder not created: {result_folder_not_created}")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    is_unix = system() != "Windows"

    run_pq(args.sugar, config, is_unix)
