import json
from pathlib import Path
from typing import Dict, List


def find_uncharacterized_protein_models(result_file: Path) -> None:
    with open(result_file, "r") as f:
        results: Dict[str, Dict[str, List[str]]] = json.load(f)

    for surr, result in results.items():
        for af_struct, metadata in result.items():
            if "uncharacterized" in metadata[0].lower():
                print(f"For surrounding {surr} found uncharacterized protein {af_struct} with description '{metadata[0]}'.")


def compare_search_results(file1: Path, file2: Path) -> None:
    with open(file1, "r") as f1:
        results1: Dict[str, Dict[str, List[str]]] = json.load(f1)

    with open(file2, "r") as f2:
        results2: Dict[str, Dict[str, List[str]]] = json.load(f2)

    print(f"The results are same: {results1 == results2}")
