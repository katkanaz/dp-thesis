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


