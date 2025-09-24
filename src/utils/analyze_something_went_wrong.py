import json


def analyze_something_went_wrong(path_to_file: Path) -> dict[str, int]:
    with open(path_to_file, "r", encoding="utf8") as file:
        wrong: list[list[str]] = json.load(file)
