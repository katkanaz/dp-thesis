"""
Script Name: structure_motif_search.py
Description: Extract input files, define residues for each input and perform structure based search.
Author: Kateřina Nazarčuková
"""


from argparse import ArgumentParser
import math
import json
from pathlib import Path
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from typing import List, Dict, Tuple, Union
from rcsbsearchapi.search import StructMotifQuery, StructureMotifResidue, AttributeQuery
import requests

from Bio.PDB.PDBParser import PDBParser
from tqdm import tqdm
from logger import logger, setup_logger

from pymol import cmd
from .perform_alignment import select_sugar

from configuration import Config
from utils.modify_struct_search_id import modify_id

GRAPHQL_ENDPOINT = "https://data.rcsb.org/graphql"


def get_sugar_ring_center(sugar: str) -> List[float]:
    """
    Locate the center of the sugar ring.

    :param sugar: Sugar which center needs to be found
    :return: The center coordinates
    """

    return cmd.centerofmass(sugar)


def measure_distances(residues: List[Tuple[str, str, str]], sugar_center: List[float], filename: str) -> List[Tuple[Tuple[str, str, str], float]]:
    """
    Measure the distane from all the residues to the sugar center.

    :param residues: The amino acids of the surrounding
    :param sugar_center: Coordinates of the sugar center
    :param filename: Name of the surrounding file which serves as name of the PyMOL object
    :return: Distances of all the residues from the sugar center
    """

    distances: List[Tuple[Tuple[str, str, str], float]] = []

    cmd.pseudoatom(object="tmp", pos=sugar_center)
    for resi, resn, chain in residues:
        atoms = cmd.get_model(f"resi {resi}").atom
        min_distance = math.inf
        
        for atom in atoms:
            distance = cmd.get_distance(f"{filename} and index {atom.index}", "tmp") # In Angstroms [Å]
            if distance < min_distance:
                min_distance = distance

        distances.append(((resi, resn, chain), min_distance))


    cmd.delete("tmp")
    return distances


def sort_distances(distances: List[Tuple[Tuple[str, str, str], float]], max_res: int) -> List[Tuple[Tuple[str, str, str], float]]:
    """
    Sort the residue distances in ascending order and keep information of the residues that are over <max_res>.

    :param distances: The distances of the residues from the sugar
    :param max_res: Allowed maximum of residues
    :return: Residues to delete
    """
    # If 2 residues same distance the one with the lower number and chain with the earlier alphabetical ID goes first
    sorted_distances = sorted(distances, key=lambda item: (item[1], int(item[0][0]), item[0][2]))
    return sorted_distances[max_res:]


def remove_residues(residues_to_remove: List[Tuple[Tuple[str, str, str], float]]) -> None:
    """
    Remove residues from the surrounding.

    :param residues_to_remove: Residues to be deleted
    """

    for (resi, resn, chain), _ in residues_to_remove:
        selection = f"chain {chain} and resi {resi} and resn {resn}"
        cmd.remove(selection)


def replace_deuterium(file_list: List[Tuple[Path, int]]) -> None:
    """
    Replace deuterium (D) with hydrogen (H)

    :param file_list: Files that need deuterium replacement
    """

    for file, _ in file_list:
        logger.info(f"Replacing deuterium for file: {file}")
        with open(file, "r") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line[76:78] == " D":
                chars = list(line)
                chars[77] = "H"
                line = "".join(chars)
            new_lines.append(line)
        with open(file, "w") as f:
            f.writelines(new_lines)


def extract_and_process_representatives(sugar: str, number: int, method: str, config: Config, input_representatives: Path, max_residues: int, file_list: Union[List[Tuple[Path, int]], None] = None) -> List[Tuple[Path, int]]:
    """
    Extract files for structure motif search.

    :param sugar: The sugar for which the representative surroundings are defined 
    :param number: The number of created clusters
    :param method: The clustering method
    :param config: Config object
    :param input_representatives: Folder to extract representatives in
    :param max_residues: Maximum of amino acids in the surrounding - necessary for struture motif search later in the process
    :file_list: Surroundings that contain deuterium (D); defaults to None
    """

    if file_list is None:
        logger.info("Extracting representatives")
    else:
        logger.info("Extracting representatives that used to have deuterium")

    with open(config.clusters_dir / "super" / f"{number}_{method}_cluster_representatives.json") as rep_file:
        representatives: dict = json.load(rep_file)
    with open(config.clusters_dir / f"{sugar}_structures_keys.json") as struct_keys_file:
        structure_keys: dict = json.load(struct_keys_file)

    more_than_max_aa = []
    deuterium_present: List[Tuple[Path, int]] = []

    file_keys = [file_key for _, file_key in representatives.items()] if file_list is None else [file[1] for file in file_list]
    for file_key in tqdm(file_keys, desc="Extracting and processing representatives"):
        path_to_surrounding_file = Path(config.filtered_surroundings_dir / structure_keys[str(file_key)])
        surrounding_file_name = path_to_surrounding_file.stem

        cmd.delete("all")
        cmd.load(path_to_surrounding_file)
        count = cmd.count_atoms("n. CA and polymer")
        sugar, sugar_selection_name = select_sugar(surrounding_file_name)
        logger.debug(f"Sugar is {sugar}")

        if count > max_residues:
            more_than_max_aa.append(surrounding_file_name)
            logger.debug(f"{surrounding_file_name} more than 10 residues!")
            try:
                sugar_center = get_sugar_ring_center(sugar_selection_name)
            except KeyError as e:
                if str(e) == "'D'":
                    deuterium_present.append((path_to_surrounding_file, file_key))
                    logger.warning(f"Found deuterium in: {path_to_surrounding_file.stem}")
                else:
                    raise e
                continue
            residues: List[Tuple[str, str, str]] = []
            cmd.iterate("n. CA and polymer", "residues.append((resi, resn, chain))", space=locals())
            logger.debug(f"Residues list: {residues}")
            
            distances = measure_distances(residues, sugar_center, surrounding_file_name)

            residues_to_remove = sort_distances(distances, max_residues)
            remove_residues(residues_to_remove)

        cmd.save(f"{input_representatives}/{surrounding_file_name}.pdb")
        cmd.delete("all")
        logger.debug(f"{surrounding_file_name} succesfully processed!")

    logger.info(f"Number of surroundings with more than {max_residues} AA: {len(more_than_max_aa)}")

    return deuterium_present


def load_representatives(config: Config) -> List[Path]:
    """
    Load the input representative surroundings for structure motif search.

    :param config: Config object
    :return: Paths to representative surroundings
    """

    representatives: List[Path] = []
    for file in sorted(Path(config.structure_motif_search_dir / "input_representatives").glob("*.pdb")):
        representatives.append(file)

    return representatives


def get_struc_name(path_to_file: Path) -> str:
    """
    Get name of the structure from the file name.

    :param path_to_file: Path to structure file
    :return: Name of the structure
    """

    return (path_to_file.name).split("_")[1]


def define_residues(path_to_file: Path, struc_name: str) -> List[StructureMotifResidue]:
    """
    Define residues for struture motif search query.

    :param path_to_file: Path to structure file
    :param struc_name: Name of the structure
    :return: List of defined residues
    :raises ValueError: If there are more than 10 resides in the surrounding
    """

    parser = PDBParser()

    structure = parser.get_structure(struc_name, path_to_file)

    models = list(structure)

    chains = list(models[0])

    # Usually the sugar has "it's own" chain meaning that all amino acid residues have chain ID for example A and the sugar has B
    # However in some files there is a chain A and then chain B which includes both sugar and amino acids
    # Sugar cannot be excluded from renumbering? # FIXME:
    sorted_chains = sorted(chains, key = lambda c: c.get_id())
    chain_id_map = {}
    key = "A"
    # TODO: Test runtime if tqdm useful
    for ch in sorted_chains:
        all_res = list(ch.get_residues())

        # Skip chains made up only of ligands or water
        if all(res.get_id()[0] != " " for res in all_res):
            continue
        chain_id_map[ch.get_id()] = key
        key = chr(ord(key) + 1)

    # TODO: Test runtime if tqdm useful
    residues = []
    for chain in chains:
        i = 1
        for residue in chain:
            residue: Residue = residue
            chain: Chain = chain
            # Excludes the sugar #FIXME: Make clearer
            if residue.get_id()[0] == " ":
                residues.append(StructureMotifResidue(struct_oper_id="1", chain_id=chain_id_map[chain.get_id()], label_seq_id=i)) # type: ignore
            i += 1

    if len(residues) > 10:
        raise ValueError(f"More than 10 residues in the surrounding: {path_to_file.name}")

    return residues


def fetch_metadata(ids: List[str]) -> Dict[str, Tuple[str, str]]:
    """
    Fetch desired structure metadata using RCSB GraphQL API.

    :param ids: IDs of structures
    :return: Computed structures with their titles and other metadata
    """

    query = """
    query getMetadata($ids: [String!]!) {
        entries(entry_ids: $ids) {
            rcsb_id
            struct {
                title
            }
            struct_keywords {
                pdbx_keywords
            }
        }
    }
    """
    variables = {"ids": ids}
    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json={"query": query, "variables": variables}
    )

    if response.status_code != 200:
        raise Exception(f"GraphQL query failed with status {response.status_code}")

    data = response.json()
    entries = data.get("data", {}).get("entries", [])
    computed_models: Dict[str, Tuple[str, str]] = {} # TODO: double check type
    # TODO: Test runtime if tqdm useful
    for entry in entries:
        rcsd_id = entry.get("rcsb_id", "UNKNOWN_ID")
        title = entry.get("struct", {}).get("title", "N/A")
        keywords_data = entry.get("struct_keywords")

        if keywords_data and isinstance(keywords_data, dict):
            keywords = keywords_data.get("pdbx_keywords", "No keywords")
        else:
            keywords = "No keywords"

        computed_models[rcsd_id] = (title, keywords)

    return computed_models


def run_query(path_to_file: Path, residues: List[StructureMotifResidue], search_results: Dict[str, Dict[str, Tuple[str, str]]]) -> None:
    """
    Run structure motif search query.

    :param path_to_file: Path to structure file
    :param residues: Defined structure residues
    :param search_results: To save search residues from all the queries
    """

    q1 = AttributeQuery(
        attribute="rcsb_comp_model_provenance.source_db",
        operator="exact_match",
        value="AlphaFoldDB",
        service="text",
        negation=False
    )

    q2 = StructMotifQuery(
        structure_search_type="file_upload",
        file_path=str(path_to_file),
        file_extension="pdb",
        residue_ids=residues,
        rmsd_cutoff=3,
        atom_pairing_scheme="ALL"
    )

    query = q1 & q2

    output: List[str] = list(query(results_verbosity="compact", return_type="assembly", return_content_type=["computational", "experimental"]))# FIXME: Returns different scores of structures when "experimental" is and is not there

    ids = [modify_id(id) for id in output]
    structures = fetch_metadata(ids)

    search_results[path_to_file.stem] = structures


def structure_motif_search(sugar: str, perform_clustering: bool, number: int, method: str, config: Config, max_residues: int) -> None:
    input_folder = config.structure_motif_search_dir / "input_representatives"
    input_folder.mkdir(exist_ok=True, parents=True)

    search_results: Dict[str, Dict[str, Tuple[str, str]]] = {}

    # FIXME: Think about keeping or removing flag
    if perform_clustering:
        deuterium_present = extract_and_process_representatives(sugar, number, method, config, input_folder, max_residues)
        if deuterium_present:
            replace_deuterium(deuterium_present)
            logger.info("Refining binding sites with replaced deuterium")
            extract_and_process_representatives(sugar, number, method, config, input_folder, max_residues, deuterium_present)
        representatives: List[Path] = load_representatives(config)
    else:
        representatives: List[Path] = list(config.filtered_surroundings_dir.glob("*.pdb"))
        logger.info("Skipping clustering, structure motif search from filtered surroundings")
    

    for file in tqdm(representatives, desc="Processing representatives"):
        struc_name = get_struc_name(file)

        try:
            logger.info(f"Performing structure motif search for {file.stem}")
            residues = define_residues(file, struc_name)
            run_query(file, residues, search_results)
        except ValueError as e:
            logger.error(f"Exception caught: {e}")


    with open(config.structure_motif_search_dir / "search_results.json", "w", encoding="utf8") as f:
        json.dump(search_results, f, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-c", "--perform_clustering", action="store_true", help="Whether to perform data clustering of filtered surroundings")
    parser.add_argument("-n", "--number", help="Number of clusters", type=int, required=True, default=20)
    parser.add_argument("-m", "--method", help="Cluster method", type=str, required=True, default="centroid")
    parser.add_argument("--max_residues", help="Maximal number of residues in a surrunding. Required by structure motif search", type=int, default=5)

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True, args)

    setup_logger(config.log_path)

    structure_motif_search(args.sugar, args.perform_clustering, args.number, args.method, config, args.max_residues)

    config.clear_current_run()
