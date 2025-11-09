import gemmi
import json

def foo(input_file):
    with open("/home/kaci/dp/utils/alternative_conformations/" + "sugar_names.json") as f:
        sugar_names = set(json.load(f)) # Set for optimalization

    structure_a = gemmi.read_structure(str(input_file))

    for model_idx, model in enumerate(structure_a):
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                if residue.name in sugar_names:
                    print(residue.name, chain.name, str(residue.seqid.num))


foo("/home/kaci/dp/data/july_2024/mmcif_files/1aa5.cif")
foo("/home/kaci/dp/data/july_2024/mmcif_files/3ai0.cif")
foo("/home/kaci/dp/data/july_2024/mmcif_files/6sd7.cif")
foo("/home/kaci/dp/data/july_2024/mmcif_files/7p43.cif")
# foo("/home/kaci/dp/data/july_2024/mmcif_files/")
# foo("/home/kaci/dp/data/july_2024/mmcif_files/")
# foo("/home/kaci/dp/data/july_2024/mmcif_files/")
