import json
from pathlib import Path
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


def compare_representatives_dirs(path_to_first_dir: Path, path_to_second_dir: Path) -> None:
    first_representatives: List[str] = []
    for file in sorted(path_to_first_dir.glob("*.pdb")):
        first_representatives.append(file.name)

    second_representatives: List[str] = []
    for file in sorted(path_to_second_dir.glob("*.pdb")):
        second_representatives.append(file.name)

    # Remove indexes - different for each run
    first_representatives = [s.partition("_")[2] for s in first_representatives]
    second_representatives = [s.partition("_")[2] for s in second_representatives]

    same = set(first_representatives) & set(second_representatives)
    print(f"Number of same files: {len(same)}")
    print(same)

    ids1 = [s.split("_")[1] for s in first_representatives]
    ids2 = [s.split("_")[1] for s in second_representatives]

    same_ids = set(ids1) & set(ids2)
    print(f"Number of same originating structures: {len(same_ids)}")
    print(same_ids)

