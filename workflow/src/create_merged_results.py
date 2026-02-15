from argparse import ArgumentParser
import json
from pathlib import Path


def main(source: list[Path], output: Path) -> None:
    print(source)
    results = {}

    for file_name in source:
        with open(file_name, "r") as f:
            data: dict = json.load(f)
            for surrounding, comp_structs in data.items():
                for struct in comp_structs:
                    if struct not in results:
                        results[struct] = {

                        }



if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--source", help="Source of the results for one sugar", type=Path, action="append", required=True)
    parser.add_argument("-o", "--output", help="Path to output file", type=Path, required=True)

    args = parser.parse_args()

    main(args.source, args.output)
