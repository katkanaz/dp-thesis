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
from typing import List, Dict
from rcsbapi.search import StructMotifQuery, AttributeQuery, StructMotifResidue
from rcsbapi.data import DataQuery

from Bio.PDB.PDBParser import PDBParser
from tqdm import tqdm
from logger import logger, setup_logger


from configuration import Config
from utils.modify_struct_search_id import modify_id
from utils.pymol_subprocess import run_pymol_subprocess


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


def define_residues(path_to_file: Path, struc_name: str) -> List[StructMotifResidue]:
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
                residues.append(StructMotifResidue(struct_oper_id="1", chain_id=chain_id_map[chain.get_id()], label_seq_id=i)) # type: ignore
            i += 1

    if len(residues) > 10:
        raise ValueError(f"More than 10 residues in the surrounding: {path_to_file.name}")

    return residues


def fetch_metadata(ids: List[str]) -> Dict[str, Dict]:
    """
    Fetch desired computed models metadata using RCSB PDB Data API.

    :param ids: IDs of computed models
    :return: Computed structures with the desired metadata.
    """

    query = DataQuery(
        input_type="entries",
        input_ids=ids,
        return_data_list=["struct.title", "software", "polymer_entities.rcsb_entity_source_organism.ncbi_scientific_name", "rcsb_ma_qa_metric_global.ma_qa_metric_global", "rcsb_comp_model_provenance.entry_id", "rcsb_accession_info.major_revision"]
    )

    result_dict = query.exec()

    comp_structures = {}
    for entry in result_dict["data"]["entries"]:

        if len(entry["polymer_entities"]) != 1:
            logger.warning(f"{entry["rcsb_id"]} expected to have 1 polymer_entity, has: {len(entry["polymer_entities"])}")
        organisms = [o["ncbi_scientific_name"] for o in entry["polymer_entities"][0]["rcsb_entity_source_organism"]]

        soft_list = [s["version"] for s in entry["software"] if s["name"] == "AlphaFold"]
        if len(soft_list) != 1:
            logger.error(f"Expected source software to be AlphaFold. Did not find AlphaFold version. len(soft_list) = {len(soft_list)}")
            raise Exception("did not find source AlphaFold version")
        af_version = soft_list[0]

        plddt = [m["value"] for m in entry["rcsb_ma_qa_metric_global"][0]["ma_qa_metric_global"] if m["type"] == "pLDDT"]
        if len(plddt) != 1:
            logger.error(f"Expected one pLDDT value. found: {len(plddt)}")
            raise Exception("did not find expected plddt value")

        comp_model_data = {
            "afdb_id": entry["rcsb_comp_model_provenance"]["entry_id"],
            "title": entry["struct"]["title"],
            "organism": organisms,
            "plddt": plddt[0],
            "af_version": af_version,
            "af_revision": entry["rcsb_accession_info"]["major_revision"]
        }
        comp_structures[entry["rcsb_id"]] = comp_model_data

    return comp_structures


def run_query(path_to_file: Path, residues: List[StructMotifResidue], search_results: Dict[str, Dict[str, Dict]]) -> None:
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
        file_format="pdb",
        residue_ids=residues,
        rmsd_cutoff=3,
        atom_pairing_scheme="ALL"
    )

    query = q1 & q2

    output = query(results_verbosity="verbose", return_type="assembly", return_content_type=["computational", "experimental"])
    assert not isinstance(output, int), "query result is of type Session"
    # FIXME: Returns different scores of structures when "experimental" is and is not there


    ids = [modify_id(comp_struct["identifier"]) for comp_struct in output] # type: ignore
    structures = fetch_metadata(ids)

    for comp_struct in output: #type: ignore
        comp_struct: Dict = comp_struct
        services = [s for s in comp_struct["services"] if s["service_type"] == "strucmotif"]
        if len(services) != 1:
            logger.error(f"Expected one strucmotif service. found: {len(services)}")
            raise Exception("did not find expected structmotif service")
        nodes = services[0]["nodes"]
        if len(nodes) != 1:
            logger.error(f"Expected one node. found: {len(nodes)}")
            raise Exception("did not find expected number of nodes")
        motifs = nodes[0]["match_context"] 
        structures[modify_id(comp_struct["identifier"])]["motifs"] = motifs 

    search_results[path_to_file.stem] = structures


def structure_motif_search(test_mode: bool, sugar: str, perform_clustering: bool, number: int, method: str, config: Config, max_residues: int) -> None:
    search_results: Dict[str, Dict[str, Dict]] = {}

    # FIXME: Think about keeping or removing flag
    if perform_clustering:
        run_pymol_subprocess("process_handlers.proximity_filtering", ["-t" if test_mode else "", "-s", sugar, "-n", str(number), "-m", method, "--max_residues", str(max_residues)])
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


    with open(config.structure_motif_search_dir / f"{sugar}_search_results.json", "w", encoding="utf8") as f:
        json.dump(search_results, f, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-t", "--test_mode", action="store_true",
                        help="Weather to run the whole process in a test mode")
    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
    parser.add_argument("-c", "--perform_clustering", action="store_true", help="Whether to perform data clustering of filtered surroundings")
    parser.add_argument("-n", "--number", help="Number of clusters", type=int, default=20)
    parser.add_argument("-m", "--method", help="Cluster method", type=str, default="centroid")
    parser.add_argument("--max_residues", help="Maximum number of residues in a surrunding. Required by structure motif search", type=int, default=10)
    parser.add_argument("--keep_current_run", help="Don't end the current run (won't delete .current_run file)", action="store_true")

    args = parser.parse_args()

    config = Config.load("config.json", args.sugar, True, args)

    setup_logger(config.log_path)

    structure_motif_search(args.test_mode, args.sugar, args.perform_clustering, args.number, args.method, config, args.max_residues)

    if not args.keep_current_run:
        Config.clear_current_run()
