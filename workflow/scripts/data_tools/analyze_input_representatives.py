from pathlib import Path

def analyze_representatives(dir1: Path, dir2: Path) -> None:
    files1 = {f.name.partition("_")[2] for f in dir1.iterdir() if f.is_file()}
    files2 = {f.name.partition("_")[2] for f in dir2.iterdir() if f.is_file()}

    only_in_1 = files1 - files2
    only_in_2 = files2 - files1
    intersection = files1 & files2

    print(f"Difference {dir1}")
    print(f"Count: {len(only_in_1)}")
    print(f"Files: {', '.join(sorted(only_in_1))}")

    print(f"Difference {dir2}")
    print(f"Count: {len(only_in_2)}")
    print(f"Files: {', '.join(sorted(only_in_2))}")

    print("Intersection")
    print(f"Count: {len(intersection)}")
    print(f"Files: {', '.join(sorted(intersection))}")

