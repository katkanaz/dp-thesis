def parse_surrounding_name(name: str) -> dict[str, str]:
    parts = name.split("_")
    return {
        "index": parts[0],
        "altloc": parts[1],
        "pdb_id": parts[2],
        "sugar": parts[3],
        "chain_num": parts[4],
        "chain_name": parts[5]
    }
