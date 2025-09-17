import json
from pathlib import Path
from datetime import datetime
import os
import pandas as pd
import subprocess
from zipfile import ZipFile

# FIXME: how to deal with the fact that patterns is too big? unzip then takes long

def get_pdb_ids_from_pq(dest_path: Path, result_file: Path) -> None:
    """
    Get PDB IDs of structures from PQ (PatternQuery) results.

    :param result_file: Path to file for writing results
    :param config: Config object
    """

    structures = pd.read_csv(dest_path / "result/structures-with-sugars/structures.csv")
    pdb_ids = structures.iloc[:,0].tolist()

    with open(result_file, "w") as f:
        json.dump(pdb_ids, f, indent=4)


def unzip_file(dest_path) -> None:
    with ZipFile(dest_path / "result.zip", "r") as zip_ref:
        zip_ref.extractall(dest_path / "result")


def get_pq_result(dest_path: Path) -> None:
    user = os.getenv("RSYNC_USER")
    assert user is not None, "RSYNC_USER is missing from environment"
    password = os.getenv("RSYNC_PASSWORD")
    assert user is not None, "RSYNC_USER is missing from environment"
    host = os.getenv("RSYNC_HOST")
    assert user is not None, "RSYNC_USER is missing from environment"

    src_path = f"{user}@{host}:/storage/brno2/home/{user}/pq-runs/2025-07-19T17-44-results/result/result.zip" # FIXME: Not abstract enough 


    cmd = [
        "/usr/bin/rsync",
        "-ratlz",
        f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
        src_path,
        dest_path
    ]

    subprocess.run(cmd, check=True)


def main() -> None:
    proj_root = f""
    dest_path = Path(f"{proj_root}/data/sugar_binding_patterns/test_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}/")
    dest_path.mkdir(exist_ok=True)
    result_file = Path(f"{proj_root}/data/sugar_binding_patterns/test_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}/pdb_ids_pq.json")

    get_pq_result(dest_path)
    unzip_file(dest_path)
    get_pdb_ids_from_pq(dest_path, result_file)



if __name__ == "__main__":
    main()
