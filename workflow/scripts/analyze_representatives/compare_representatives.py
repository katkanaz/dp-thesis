import json
from pathlib import Path
import re
from typing import List


def compare_repres_dir_with_json(path_to_dir: Path, path_to_json: Path) -> None:
    dir_representatives: List[str] = []
    for file in sorted(path_to_dir.glob("*.pdb")):
        dir_representatives.append(file.name)

    with open(path_to_json) as f:
        json_representatives = json.load(f)

    dir_representatives = [s.partition("_")[2] for s in dir_representatives]
    json_representatives = ["0_" + s.partition("_")[2] for s in json_representatives]

    same = set(dir_representatives) & set(json_representatives)
    print(f"Number of same files: {len(same)}")
    print(same)


def compare_dirs_after_filtration(path_to_first_dir: Path, path_to_second_dir: Path) -> None:
    first_dir_files: List[str] = []
    for file in sorted(path_to_first_dir.glob("*.pdb")):
        first_dir_files.append(file.name)

    second_dir_files: List[str] = []
    for file in sorted(path_to_second_dir.glob("*.pdb")):
        second_dir_files.append(file.name)

    # Remove indexes - different for each run
    first_dir_files = [s.partition("_")[2] for s in first_dir_files]
    second_dir_files = [s.partition("_")[2] for s in second_dir_files]

    same = set(first_dir_files) & set(second_dir_files)
    print(f"Number of same files: {len(same)}")
    print(same)

    ids1 = [s.split("_")[1] for s in first_dir_files]
    ids2 = [s.split("_")[1] for s in second_dir_files]

    same_ids = set(ids1) & set(ids2)
    print(f"Number of same originating structures: {len(same_ids)}")
    print(same_ids)


def compare_raw_surrs_no_altloc(path_to_first_dir: Path, path_to_second_dir: Path) -> None:
    first_dir_files: List[str] = []
    for file in sorted(path_to_first_dir.glob("*.pdb")):
        first_dir_files.append(file.name)

    second_dir_files: List[str] = []
    for file in sorted(path_to_second_dir.glob("*.pdb")):
        second_dir_files.append(file.name)

    # Remove altloc identifiers if present
    first_dir_files = [re.sub(r'^\d+_', '', file) for file in first_dir_files]
    second_dir_files = [re.sub(r'^\d+_', '', file) for file in first_dir_files]

    same = set(first_dir_files) & set(second_dir_files)
    print(f"Number of same files: {len(same)}")
    # print(same)

    ids1 = [s.split("_")[0] for s in first_dir_files]
    ids2 = [s.split("_")[0] for s in second_dir_files]

    same_ids = set(ids1) & set(ids2)
    print(f"Number of same originating structures: {len(same_ids)}")
    # print(same_ids)

