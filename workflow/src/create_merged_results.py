from argparse import ArgumentParser
import json
from pathlib import Path

from utils.parse_surrounding_name import parse_surrounding_name


def create_merged_results(source: list[Path], output: Path) -> None:
    merged = {}

    for file_name in source:
        with open(file_name, "r") as f:
            results: dict = json.load(f)
            for surrounding, comp_structs in results.items():
                for struct, data in comp_structs.items():
                    if struct not in merged:
                        merged[struct] = {
                            "pdb_id": struct,
                            "afdb_id": data["afdb_id"],
                            "title": data["title"],
                            "organism": data["organism"],
                            "plddt": data["plddt"],
                            "af_version": data["af_version"],
                            "af_revision": data["af_revision"],
                            "motifs": []
                        }
                    surrounding_name = parse_surrounding_name(surrounding)
                    motif_metadata = {"surrounding": surrounding, "sugar": surrounding_name["sugar"], "original_struct": surrounding_name["pdb_id"]}
                    merged[struct]["motifs"].extend(map(lambda x: {**motif_metadata, **x}, data["motifs"]))

    with open(output, "w") as f:
        json.dump(list(merged.values()), f, indent=4)



if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--source", help="Source of the results for one sugar", type=Path, action="append", required=True)
    parser.add_argument("-o", "--output", help="Path to output file", type=Path, required=True)

    args = parser.parse_args()

    create_merged_results(args.source, args.output)
