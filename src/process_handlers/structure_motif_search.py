"""
Script Name: structure_motif_search.py
Description: Extract input files, define residues for each input and perform structure based search.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import json
from pathlib import Path
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from typing import List
from rcsbsearchapi.search import StructMotifQuery, StructureMotifResidue, AttributeQuery
import shutil

from Bio.PDB.PDBParser import PDBParser
from logger import logger, setup_logger

from configuration import Config


def extract_representatives(sugar: str, align_method: str, num: int, min_residues: int, method: str, config: Config, input_representatives: Path) -> None:
    #FIXME: fix the docs
    """
    Extract files for structure motif search

    :param sugar: The sugar for which representative binding sites are being defined
    :param align_method: The PyMOL command that was used for alignment
    :param representatives_file: The file containing the representative binding sites ids
    :param config: Config object
    :param input_folder: Folder to extract representatives in
    """

    filtered_binding_sites: Path = config.filtered_binding_sites_dir / f"min_{min_residues}_aa"

    with open(config.clusters_dir / align_method / f"{num}_{method}_cluster_representatives.json") as rep_file:
        representatives: dict = json.load(rep_file)
    with open(config.clusters_dir / f"{sugar}_structures_keys.json") as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)

    for num, file_key in representatives.items():
        binding_site_file_name = structure_keys[str(file_key)]
        shutil.copyfile((filtered_binding_sites / binding_site_file_name), (input_representatives / binding_site_file_name))


def load_representatives(config: Config) -> List[Path]:
    # TODO: Add docs
    representatives = []
    for file in sorted(Path(config.structure_motif_search_dir / "input_representatives").glob("*.pdb")):
        representatives.append(file)

    return representatives


def get_struc_name(path_to_file: Path) -> str:
    # TODO: Add docs
    return (path_to_file.name).split("_")[1]


def define_residues(path_to_file: Path, struc_name: str) -> List[StructureMotifResidue]:
    # TODO: Add docs
    parser = PDBParser()

    structure = parser.get_structure(struc_name, path_to_file)

    models = list(structure)
    if len(models) < 1:
        raise ValueError("More than one model in the structure!")

    chains = list(models[0])

    sorted_chains = sorted(chains, key = lambda c: c.get_id())
    chain_id_map = {}
    key = "A"
    for ch in sorted_chains:
        chain_id_map[ch.get_id()] = key
        key = chr(ord(key) + 1)

    residues = []
    for chain in chains:
        i = 1
        for residue in chain: # NOTE: also possible to only iterate over all residues in a model
            residue: Residue = residue
            chain: Chain = chain
            # Excludes fucose
            if residue.get_id()[0] == " ":
                residues.append(StructureMotifResidue(struct_oper_id="1", chain_id=chain_id_map[chain.get_id()], label_seq_id=i)) # type: ignore
                i += 1

    if len(residues) > 10:
        raise ValueError(f"More than 10 residues in the binding site: {path_to_file.name}")

    return residues


def run_query(path_to_file: Path, residues: List[StructureMotifResidue]) -> None:
    # TODO: Add docs
    q1 = AttributeQuery(attribute="rcsb_comp_model_provenance.source_db", operator="exact_match",value="AlphaFoldDB", service="text", negation=False)
    q2 = StructMotifQuery(structure_search_type="file_upload", file_path=str(path_to_file), file_extension="pdb", residue_ids=residues, rmsd_cutoff=3, atom_pairing_scheme="ALL")

    query = q1 & q2

    output = list(query(return_type="assembly", return_content_type=["computational", "experimental"]))# NOTE: Returns different scores of structures when "experimental" is and is not there

    #TODO: how to handle multiple surroundings, each a file
    with open(config.structure_motif_search_dir / "search_result.json", "w", encoding="utf8") as f:
        json.dump(output, f, indent=4)


def structure_motif_search(config: Config) -> None:
    logger.info("Structure motif search not automated yet")
    input_folder = config.structure_motif_search_dir / "input_representatives"
    input_folder.mkdir(exist_ok=True, parents=True)


    # Files to test
    # path_to_file = Path("../debug/sms_query_test/369_7khu_FUC_6_C.pdb")

    # extract_representatives(args.sugar, args.align_method, args.number, min_residues, args.method, config, input_folder)
    # struc_name = get_struc_name(path_to_file)
    # run_query(path_to_file, define_residues(path_to_file, struc_name))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", type=str,
                        choices=["super", "align"], required=True)
    parser.add_argument("-n", "--number", help="Number of clusters", type=str, required=True)
    parser.add_argument("-m", "--method", help="Cluster method", type=str, required=True)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True)

    setup_logger(config.log_path)

    structure_motif_search(config)

    config.clear_current_run()
