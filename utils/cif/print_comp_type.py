from pathlib import Path

import gemmi

def remove_non_sugar_residues(input_cif_path):
    doc = gemmi.cif.read(input_cif_path)

    for block in doc:
        block_comp_type = block.find_value('_chem_comp.type')

        print(f"Block-level _chem_comp.type: {block_comp_type}")

if __name__ == "__main__":
    remove_non_sugar_residues(Path("../data/july_2024/components/components.cif.gz"))
