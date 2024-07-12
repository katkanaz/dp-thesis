from csv import DictReader
import json

from config import Config


def get_pdb_ids_with_rscc(config: Config) -> None:
    """
    Get the PDB IDs of structures whose residues have RSCC values

    :param config: Config object
    """

    with open(config.validation_results / "all_rscc_and_resolution.csv") as f:
        rscc = DictReader(f) #FIXME: Use pandas
        pdb_ids = set()
        for row in rscc:
            pdb_ids.add(row["pdb"])
    with open(config.validation_results / "pdbs_with_rscc_and_resolution.json", "w") as f:
        json.dump(list(pdb_ids), f, indent=4)


def remove_O6(config: Config, no_o6_mmcif) -> None:
    """
    Remove O6 atom of NAG, GAL, MAN, GLC and BGC from the structures

    :param config: Config object
    """

    with open(config.validation_results / "pdbs_with_rscc_and_resolution.json") as f:
        pdb_ids_of_interest = json.load(f)
    for pdb in pdb_ids_of_interest:
        with (config.mmcif_files / f"{pdb.lower()}.cif").open() as f:
            file = f.readlines()
        with (no_o6_mmcif / f"{pdb.lower()}.cif").open("w") as f:
            for line in file:
                if line.startswith("HETATM"): #FIXME: Refactor if else
                    if "MAN" in line or "NAG" in line or "GAL" in line or "GLC" in line or "BGC" in line:
                        if "O6" in line:
                            continue
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                else:
                    f.write(line)


if __name__ == "__main__":
    config = Config.load("config.json")

    no_o6_mmcif = config.data_folder / "no_o6_mmcif"
    no_o6_mmcif.mkdir(exist_ok=True, parents=True)

    get_pdb_ids_with_rscc(config)
    remove_O6(config, no_o6_mmcif)
