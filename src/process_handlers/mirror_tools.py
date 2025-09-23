import json
from pathlib import Path
import os
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
    # TODO: Add docs
    user = os.getenv("RSYNC_USER")
    assert user is not None, "RSYNC_USER is missing from environment"
    password = os.getenv("RSYNC_PASSWORD")
    assert password is not None, "RSYNC_PASSWORD is missing from environment"
    host = os.getenv("RSYNC_HOST")
    assert host is not None, "RSYNC_HOST is missing from environment"

    src_path = f"{user}@{host}:/storage/brno2/home/{user}/pq-runs/2025-07-19T17-44-results/result/result.zip" # FIXME: Not abstract enough 
    dest_path = Path(config.sugar_binding_patterns_dir)


    cmd = [
        "/usr/bin/rsync",
        "-ratlz",
        f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
        src_path,
        dest_path
    ]

    subprocess.run(cmd, check=True)


def create_file_list(config: Config, pdb_ids: set[str]) -> None:
    # TODO: Add docs
    with open(config.run_data_dir / "file_list.txt", "w", encoding="utf8") as f:
        for pdb_id in pdb_ids:
            f.write(f"{pdb_id}.cif.gz\n")


def download_structures_from_mirror(dest_path: Path, file_list_path: Path) -> None:
    # TODO: Add docs
    user = os.getenv("RSYNC_USER")
    assert user is not None, "RSYNC_USER is missing from environment"
    password = os.getenv("RSYNC_PASSWORD")
    assert password is not None, "RSYNC_USER is missing from environment"
    host = os.getenv("RSYNC_HOST")
    assert host is not None, "RSYNC_USER is missing from environment"

    src_path = f"{user}@{host}:/storage/brno2/home/{user}/pdb-mirror/"

    logger.info("Downloading validation files")

    cmd = [
        "/usr/bin/rsync",
        "-ratl",
        f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
        f"--files-from={file_list_path}",
        src_path,
        dest_path
    ]

    subprocess.run(cmd, check=True)
