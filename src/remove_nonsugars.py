#TODO: Add to run_mv
import gemmi

from config import Config


# Before running MV
def remove_nonsugar_residues(config: Config) -> None:
    """
    Remove all the non-sugar residues from the model mmCIF file

    :param config: Config object
    """
    doc = gemmi.cif.read(str(config.data_folder / "components.cif.gz"))
    for i in range(len(doc) - 1, -1, -1): 
        comp_type = doc[i].find_value('_chem_comp.type')
        if "saccharide" not in comp_type.lower(): 
            del doc[i]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20
    doc.write_file(str(config.data_folder / "components_sugars_only.cif"), options)

if __name__ == "__main__":
    config = Config.load("config.json")

    remove_nonsugar_residues(config)
