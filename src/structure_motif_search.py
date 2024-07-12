from argparse import ArgumentParser
import json
from pathlib import Path
import shutil

from config import Config


def extract_representatives(sugar: str, align_method: str, representatives_file: str, config: Config, input_folder: Path) -> None:
    """
    Extract files for structure motif search

    :param sugar: The sugar for which representative binding sites are being defined
    :param align_method: The PyMOL command that was used for alignment
    :param representatives_file: The file containing the representative binding sites ids
    :param config: Config object
    :param input_folder: Folder to extract representatives in
    """

    path_to_file: Path = config.binding_sites / f"{sugar}_fixed_5"

    with open(config.results_folder / "clusters" / sugar / align_method / representatives_file) as rep_file:
        representatives: dict = json.load(rep_file)
    with open(config.results_folder / "clusters" / sugar / f"{sugar}_structures_keys.json") as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)

    for _, file_key in representatives.items():
        structure = structure_keys[str(file_key)]
        shutil.copyfile((path_to_file / structure), (input_folder / structure))


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-f", "--file", help="File containing the keys of the representative binding sites", type=str, required=True)
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", type=str,
                        choices=["super", "align"], required=True)

    args = parser.parse_args()

    config = Config.load("config.json")
    input_folder = (config.results_folder / "structure_motif_search" / "input_representatives" / args.sugar)
    input_folder.mkdir(exist_ok=True, parents=True)

    extract_representatives(args.sugar, args.align_method, args.file, config, input_folder)

#TODO: implement advanced search api
