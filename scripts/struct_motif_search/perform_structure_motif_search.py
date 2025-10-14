import json
from pathlib import Path
from Bio.PDB.Chain import Chain
from Bio.PDB.Residue import Residue
from typing import List, Dict, Tuple
from rcsbsearchapi.search import StructMotifQuery, StructureMotifResidue, AttributeQuery
import requests

from Bio.PDB.PDBParser import PDBParser

from src.utils.modify_struct_search_id import modify_id

GRAPHQL_ENDPOINT = "https://data.rcsb.org/graphql"


def load_representatives(path_to_repres_dir: Path) -> List[Path]:
    """
    Load the input representative surroundings for structure motif search.

    :param path_to_repres_dir: Path to the directory with the representatives
    :return: Paths to representative surroundings
    """

    representatives: List[Path] = []
    for file in sorted(path_to_repres_dir.glob("*.pdb")):
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
    # Sugar cannot be excluded from renumbering # FIXME:
    sorted_chains = sorted(chains, key = lambda c: c.get_id())
    chain_id_map = {}
    key = "A"
    for ch in sorted_chains:
        all_res = list(ch.get_residues())

        # Skip chains made up only of ligands or water
        if all(res.get_id()[0] != " " for res in all_res):
            continue
        chain_id_map[ch.get_id()] = key
        key = chr(ord(key) + 1)

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


def structure_motif_search(path_to_repres_dir: Path, path_to_search_results: Path) -> None:
    search_results: Dict[str, Dict[str, Tuple[str, str]]] = {}

    representatives: List[Path] = load_representatives(path_to_repres_dir)
    

    for file in representatives:
        struc_name = get_struc_name(file)

        try:
            print(f"Performing structure motif search for {file.stem}")
            residues = define_residues(file, struc_name)
            run_query(file, residues, search_results)
        except ValueError as e:
            print(f"Exception caught: {e}")


    with open(path_to_search_results / "search_results.json", "w", encoding="utf8") as f:
        json.dump(search_results, f, indent=4)

