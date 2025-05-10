def modify_id(id: str) -> str:
    parts = id.split("-")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Invalid ID format: '{id}'. Expected format: 'XXXX-deposited'")
    return parts[0]

if __name__ == "__main__":
    modify_id("AF_AFO31908F1-deposited")
