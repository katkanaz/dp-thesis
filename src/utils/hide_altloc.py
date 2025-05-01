from typing import Dict, List
# NOTE: can check if 4 letters are returned, their case?


def remove_altloc_from_id(pdb_id: str) -> str:
    parts: List[str] = pdb_id.split("_")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Invalid PDB ID format: '{pdb_id}'. Expected format: 'X_XXXX'")
    return parts[1]

def find_residue_any_altloc(modified_ligands: Dict, unmodified_pdb_id: str, residue: Dict) -> bool:
    for modified_id in get_possible_altloc_file_names(unmodified_pdb_id):
        value = modified_ligands.get(modified_id)
        if value is not None and residue in value:
            return True
    
    return False

def get_possible_altloc_file_names(pdb_id: str) -> List[str]:
    return [f"0_{pdb_id}", f"A_{pdb_id}", f"B_{pdb_id}"]



if __name__ == "__main__":
    test1 = remove_altloc_from_id("0_12ED")
    test2 = remove_altloc_from_id("A_2345")
    print(test1, test2)
    # remove_altloc_from_id("B_1ERD")
    # remove_altloc_from_id("12ED")
    # remove_altloc_from_id("12ED_")
    # remove_altloc_from_id("_12ED")
    # remove_altloc_from_id("A_abcd")
