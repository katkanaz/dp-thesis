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
from rcsbsearchapi.search import StructMotifQuery, StructureMotifResidue, AttributeQuery
import shutil

from Bio.PDB.PDBParser import PDBParser
from logger import logger, setup_logger

from configuration import Config


# def extract_representatives(sugar: str, align_method: str, num: int, method: str, config: Config, input_folder: Path) -> None:
#     """
#     Extract files for structure motif search
#
#     :param sugar: The sugar for which representative binding sites are being defined
#     :param align_method: The PyMOL command that was used for alignment
#     :param representatives_file: The file containing the representative binding sites ids
#     :param config: Config object
#     :param input_folder: Folder to extract representatives in
#     """
#
#     path_to_file: Path = config.binding_sites / f"{sugar}_fixed_5"
#
#     with open(config.results_folder / "clusters" / sugar / align_method / f"{num}_{method}_cluster_representatives.json") as rep_file:
#         representatives: dict = json.load(rep_file)
#     with open(config.results_folder / "clusters" / sugar / f"{sugar}_structures_keys.json") as struct_keys_file:
#         structure_keys: dicutil.copyfile((path_to_file / structure), (input_folder / structure))


# def load_representatives(config: Config) -> List[Path]:
    #TODO: Add docs
    # representatives = []
    # for file in sorted(Path("../results/structure_motif_search/input_representatives/FUC/").glob("*.pdb")):
        # representatives.append(file)

    # return representatives


def get_struc_name(path_to_file: Path) -> str:
    #TODO: Add docs
    return (path_to_file.name).split("_")[1]


def define_residues(path_to_file: Path, struc_name: str) -> list:
    #TODO: Add docs
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
        for residue in chain: #NOTE: also possible to only iterate over all residues in a model
            residue: Residue = residue
            chain: Chain = chain
            # Excludes fucose
            if residue.get_id()[0] == " ":
                residues.append(StructureMotifResidue(struct_oper_id="1", chain_id=chain_id_map[chain.get_id()], label_seq_id=i)) # type: ignore
                i += 1

    if len(residues) > 10:
        raise ValueError(f"More than 10 residues in the binding site: {path_to_file.name}")

    return residues


def run_query(path_to_file: Path, residues: list):
    #TODO: Add docs
    q1 = AttributeQuery(attribute="rcsb_comp_model_provenance.source_db", operator="exact_match",value="AlphaFoldDB", service="text", negation=False)
    q2 = StructMotifQuery(structure_search_type="file_upload", file_path=str(path_to_file), file_extension="pdb", residue_ids=residues, rmsd_cutoff=3, atom_pairing_scheme="ALL")

    query = q1 & q2

    # print(query.to_json())
    logger.info(list(query(return_type="assembly", return_content_type=["computational", "experimental"]))) #NOTE: Returns different scores of structures when "experimental" is and is not there


def structure_motif_search():
    # Files to test
    # path_to_file = Path("../results/structure_motif_search/input_representatives/FUC/140_3lei_FUC_1186_A.pdb")
    # path_to_file = Path("../results/structure_motif_search/input_representatives/FUC/511_7c38_FUC_404_B.pdb")
    # path_to_file = Path("../results/structure_motif_search/input_representatives/GAL/1695_8axi_GAL_602_A.pdb")
    # path_to_file = Path("../results/structure_motif_search/input_representatives/GAL/290_2bzd_GAL_1649_B.pdb")

    # path_to_file = Path("../debug/sms_query_test/369_7khu_FUC_6_C.pdb")
    # path_to_file = Path("../debug/sms_query_test/426_2nzy_FUC_4002_B.pdb")
    path_to_file = Path("../debug/sms_query_test/523_1qot_FUC_2_H.pdb")


    struc_name = get_struc_name(path_to_file)
    run_query(path_to_file, define_residues(path_to_file, struc_name))


#TODO: check if original structure is returned

if __name__ == "__main__":
    # parser = ArgumentParser()
    #
    # parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    # parser.add_argument("-a", "--align_method", help="PyMOL cmd for the calculation of RMSD", type=str,
    #                     choices=["super", "align"], required=True)
    # parser.add_argument("-n", "--number", help="Number of clusters", type=str, required=True)
    # parser.add_argument("-m", "--method", help="Cluster method", type=str, required=True)
    #
    # # args = parser.parse_args()

    current_run = Config.get_current_run()
    # data_run = Config.get_data_run()
    config = Config.load("config.json", args.sugar, current_run, data_run)

    setup_logger(config.log_path)

    input_folder = config.structure_motif_search_dir / "input_representatives"
    input_folder.mkdir(exist_ok=True, parents=True)

    # extract_representatives(args.sugar, args.align_method, args.number, args.method, config, input_folder)
    structure_motif_search()

    config.clear_current_run()
