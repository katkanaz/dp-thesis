import json
from pathlib import Path
from collections import Counter
from typing import List, Counter


def analyze_something_went_wrong(path_to_file: Path) -> Counter:
    with open(path_to_file, "r", encoding="utf8") as file:
        wrong: List[List[str]] = json.load(file)

    problematic = Counter(string for sublist in wrong for string in sublist)

    # threshold = 2
    threshold = 104
    over_threshold = {word: count for word, count in problematic.items() if count > threshold}
    print(over_threshold)

    return problematic

# How many surroundings from which structure
def get_pdb_ids_of_problematic(counter: Counter[str]) -> Counter:
    pdb_ids = Counter(key.split("_")[2] for key in counter.keys())

    print(pdb_ids)
    return(pdb_ids)


