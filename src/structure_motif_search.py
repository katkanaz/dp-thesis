from argparse import ArgumentParser
import json
from pathlib import Path
import shutil

CLUSTERS_FOLDER = Path("/Volumes/YangYang/diplomka/results") / "clusters"
BS_FOLDER = Path("/Volumes/YangYang/diplomka/results") / "binding_sites"

SMS_FOLDER = Path("/Volumes/YangYang/diplomka/results") / "structure_motif_search"
SMS_FOLDER.mkdir(exist_ok=True, parents=True)
INPUT_FOLDER = Path("/Volumes/YangYang/diplomka/results/structure_motif_search") / "input_representatives"
INPUT_FOLDER.mkdir(exist_ok=True, parents=True) #TODO: add sugar folder


def extract_representatives(sugar: str, align_method: str, representatives_file: str) -> None:
    """Extract files for structure motif search

    :param str sugar: The sugar for which representative binding sites are being defined
    :param str align_method: The PyMOL command that was used for alignment
    :param str representatives_file: The file containing the representative binding sites ids
    """
    path_to_file: Path = BS_FOLDER / f"{sugar}_fixed_5"

    with open(CLUSTERS_FOLDER / sugar / align_method / representatives_file) as rep_file:
        representatives: dict = json.load(rep_file)
    with open(CLUSTERS_FOLDER / sugar / f"{sugar}_structures_keys.json") as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)
    
    for num, file_key in representatives.items():
        structure = structure_keys[str(file_key)]
        shutil.copyfile((path_to_file / structure), (INPUT_FOLDER / structure)) #FIXME: but the sugar dir doesnt exist


if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("-f", "--file", help="File containing the keys of the representative binding sites", type=str, required=True)
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", type=str,
                        choices=["super", "align"], required=True)

    args = parser.parse_args()

    extract_representatives(args.sugar, args.align_method, args.file)

#TODO: implement advanced search api