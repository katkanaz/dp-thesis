import json
from pathlib import Path
import os
from typing import Set, Tuple
import pandas as pd
import subprocess


from logger import logger
from configuration import Config


def get_pdb_ids_from_pq(src_path: Path, result_file: Path) -> None:
    """
    Get PDB IDs of structures from PQ (PatternQuery) results.

    :param result_file: Path to file for writing results
    :param config: Config object
    """

    structures = pd.read_csv(src_path)
    pdb_ids = structures.iloc[:,0].tolist()

    with open(result_file, "w") as f:
        json.dump(pdb_ids, f, indent=4)


def get_pq_result(config: Config) -> None:
    """
    Retrieve PatternQuery result archive from the remote host via rsync.

    :param config: Config object
    """

    user, password, host = get_rsync_info() 

    src_path = f"{user}@{host}:/storage/brno2/home/{user}/pq-runs/2025-07-19T17-44-results/result/result.zip" # FIXME: Not abstract enough 
    dest_path = Path(config.sugar_binding_patterns_dir)

    logger.info("Downloading PQ results")

    cmd = [
        "/usr/bin/rsync",
        "-ratlz",
        f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
        src_path,
        dest_path
    ]

    subprocess.run(cmd, check=True) # TODO: add runtimeerror


def create_file_list(config: Config, pdb_ids: Set[str], file_name: str, extension: str) -> Path:
    """
    Create a text file containing file names based on <pdb_ids> to download for rsync.

    :param config: Config object
    :param pdb_ids: IDs of structures to create the file contents
    :param file_name: Name of the file to save the file list into
    :param extension: File extension of the files to download
    :return: Path to file list
    """

    logger.info("Creating file list for rsync")

    with open(config.run_data_dir / file_name, "w", encoding="utf8") as f:
        for pdb_id in pdb_ids:
            f.write(f"{pdb_id}{extension}\n")

    return config.run_data_dir / file_name 


def get_rsync_info() -> Tuple[str, str, str]:
    # TODO: add docs
    user = os.getenv("RSYNC_USER")
    assert user is not None, "RSYNC_USER is missing from environment"
    password = os.getenv("RSYNC_PASSWORD")
    assert password is not None, "RSYNC_USER is missing from environment"
    host = os.getenv("RSYNC_HOST")
    assert host is not None, "RSYNC_USER is missing from environment"

    return user, password, host


def download_from_mirror(src_dir: str, dest_path: Path, file_list_path: Path) -> None:
    # TODO: add docs
    user, password, host = get_rsync_info() 

    src_path = f"{user}@{host}:/storage/brno2/home/{user}/pdb-mirror/{src_dir}"

    cmd = [
        "/usr/bin/rsync",
        "-ratl",
        f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
        f"--files-from={file_list_path}",
        src_path,
        dest_path
    ]

    subprocess.run(cmd, check=True) # TODO: add runtimeerror
 # FIXME: catch if rsync skips missing files

def download_structures_from_mirror(config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
    """
    Retrieve mmCIF structure files from the remote host via rsync.

    :param config: Config object
    :param pdb_ids: IDs of structures to use for creating the file list 
    :param dest_path: Download destination directory
    """

    file_list_path = create_file_list(config, pdb_ids, "structures_file_list.txt", ".cif.gz")
    logger.info("Downloading structures files")
    download_from_mirror("structures", dest_path, file_list_path)


def download_validation_files_from_mirror(config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
    """
    Retrieve XML validation files from the remote host via rsync.

    :param config: Config object
    :param pdb_ids: IDs of structures to use for creating the file list 
    :param dest_path: Download destination directory
    """

    file_list_path = create_file_list(config, pdb_ids, "validation_file_list.txt", ".xml.gz")
    logger.info("Downloading validation files")
    download_from_mirror("validation-files", dest_path, file_list_path)

