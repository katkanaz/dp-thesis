from pathlib import Path

import gemmi

RESULTS_FOLDER = Path("/Volumes/YangYang/diplomka") / "results"
DATA_FOLDER = Path("/Volumes/YangYang/diplomka") / "data"

 
# before running MV
def remove_nonsugar_residues() -> None:
    #TODO: add docs
    """
    Remove all non-saccharide residues from the model mmCIF file.
    """
    doc = gemmi.cif.read(str(DATA_FOLDER / "components.cif.gz"))
    for i in range(len(doc) - 1, -1, -1): 
        comp_type = doc[i].find_value('_chem_comp.type')
        if "saccharide" not in comp_type.lower(): 
            del doc[i]
    
    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20
    doc.write_file(str(DATA_FOLDER / "components_gemmi_0_6_4.cif"), options) #FIXME

if __name__ == "__main__":
    remove_nonsugar_residues()