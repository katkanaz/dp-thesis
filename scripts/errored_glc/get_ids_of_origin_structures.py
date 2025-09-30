import os

def process_file(txt_path):
    with open(txt_path, "r") as f:
        lines = f.read().splitlines()

    items = set()
    for line in lines:
        if not line.strip():
            continue
        filename = os.path.basename(line.strip())
        parts = filename.split("_")
        if len(parts) > 2:
            items.add(parts[2])

    items_list = sorted(items)

    print(f"Count: {len(items_list)}")
    print(",".join(items_list))


process_file("matched_files.txt")
