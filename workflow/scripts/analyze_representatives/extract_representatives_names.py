import json
from pathlib import Path


def representatives_to_json(path_to_repres_file: Path, path_to_struct_keys_file: Path, path_to_json: Path) -> Path:
    with open(path_to_repres_file) as rep_file:
        representatives: dict = json.load(rep_file)
    with open(path_to_struct_keys_file) as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)

    surroundings = []
    for _, file_key in representatives.items():
        surroundings.append(structure_keys[str(file_key)])

    with open(path_to_json, "w") as f:
        json.dump(surroundings, f, indent=4)

    return path_to_json

