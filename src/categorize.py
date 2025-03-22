"""
Script Name: categorize.py
Description: Categorize sugar residues from all structures to separate the lignads.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


import json
from typing import List, Dict, Set, Union

import gemmi
from gemmi.cif import Block, Table  # type: ignore
from logger import logger, setup_logger

from configuration import Config

ligands = {}  # all ligands from all structures
glycosylated = {}  # all glycosylated residues according to conn category from all structures
close_contacts = {}  # all sugar residues from close contacts which are not in conn

all_residues = {}  # all sugar residues from all structures

# The sum of all residues from ligands, glycosylated and close_contacts
# should be equal to number of residues in all_residues
# but this does not work for the sum of the pdb structures because
# there can be ligand and also glycosylation and close_contact in one structure.
# To make sure the script works properly, here are the control lists of pdb structures
# for every group, to check whether the sum is right.

pdb_only_ligands = []
pdb_only_glycosylated = []
pdb_only_close_contacts = []

pdb_ligand_glycosylated = []
pdb_ligand_close_contacts = []
pdb_glycosylated_close_contacts = []
pdb_lig_glyc_close = []


res_gycosyl_residue_not_1 = []

# some structures have sugars, but they are listed in the wrong category
# so it is not possible to automatize the search - they are excluded
pdb_sugars_in_wrong_category = set()

# after remediation of PDB database, all glycosylations should be anotated
# in struct_conn.pdbx_role but some are still missing
pdb_not_anotated_glycosylation = set()

# how many residues exists in different conformations
overall_conformers = []


AMINO_ACIDS = [
    "Ala", "Cys", "Asp", "Glu", "Phe",
    "Gly", "His", "Ile", "Lys", "Leu",
    "Met", "Asn", "Pro", "Gln", "Arg",
    "Ser","Thr", "Val", "Trp", "Tyr",
]

SUGAR_NAMES = []


def extract_sugars(table: Table) -> List[Dict[str, str]]:
    """
    Gets a list of dictionaries, in which one dictionary represents single
    sugar residue present in the given table (either monosacharide or one
    residue form oligosaccharide).

    :param table: Monosaccharide or oligosaccharide table to extract sugars from
    :return: List of sugars extracted from monosaccharide or oligosaccharide table
    """

    extracted_sugars = []
    # there can be more conformers for some residues, and sometimes it
    # means there will be two residues with the same num and chain,
    # but different name listed in the mmCIF file. PQ can find only the first one.
    conformers = []
    for row in table:
        if row[0] in SUGAR_NAMES:
            res = f"{row[1]} {row[2]}"
            if res not in conformers:
                conformers.append(res)
                extracted_sugars.append(
                    {"name": row[0], "num": row[1], "chain": row[2]}
                )
            else:
                overall_conformers.append(res)

    return extracted_sugars


def remove_connections(block: Block, mono: List[Dict[str, str]], oligo: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Remove glycosylated residues from mono and oligo (modify the lists in place)
    and return list of glycosylated residues (according to conn)

    :param block: mmCIF file block
    :param mono: List of monosaccharides
    :param oligo: List of oligosaccharides
    :return: List of glycosylated residues
    """

    glycosylated_residues = []  # glycosylated residues according to conn

    # chain of the glycosylated residue that is part of the oligosacharide
    # so it is possible to remove all residues from that chain
    glycosylated_oligo_chains = set()

    conn = block.find(
        "_struct_conn.",
        [
            "conn_type_id",
            "ptnr1_auth_comp_id",
            "ptnr2_auth_asym_id",
            "ptnr2_auth_comp_id",
            "ptnr2_auth_seq_id",
            "?pdbx_role",
        ]
    )
    has_role = conn.has_column(5)
    if not has_role:
        pdb_not_anotated_glycosylation.add(block.name)
    for row in conn:
        # only covalent connection between AK and sugar are relevant
        if (row[0] == "covale" and row[1].capitalize() in AMINO_ACIDS and row[3] in SUGAR_NAMES):
            res = {"name": row[3], "num": row[4], "chain": row[2]}

            if res in mono:
                glycosylated_residues.append(res)  # save the glycosylated mono
                mono.remove(res)  # remove it from the original list where we want only ligands

                if has_role and "glycosyl" not in row[5].lower():
                    pdb_not_anotated_glycosylation.add(block.name)

            elif res in oligo:
                glycosylated_oligo_chains.add(res["chain"])  # save the letter of the chain

                if res["num"] != "1":
                    res_gycosyl_residue_not_1.append(f"{block.name}_{res['name']}_{res['num']}_{res['chain']}")

                if not has_role:
                    pdb_not_anotated_glycosylation.add(block.name)
                else:
                    if "glycosyl" not in row[5].lower():
                        pdb_not_anotated_glycosylation.add(block.name)


    # add the whole glycosylated oligosacharide to glycosylated_residues
    # and remove it from the original list where we want only ligands
    for i in range(len(oligo) - 1, -1, -1):
        if oligo[i]["chain"] in glycosylated_oligo_chains:
            glycosylated_residues.append(oligo[i])
            del oligo[i]

    return glycosylated_residues


def remove_close_contacts(block: Block, mono: List[Dict[str, str]], oligo: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Close contacts category lists pairs of atoms from all residues, which are in so close proximity
    we cannot be sure whether there is or is not a bond. Sometimes the residues from which the pair is
    are also listed in the conn category, so we assume there is a connection. Otherwise, we treat them as
    a separate category in order to not include potential glycosylation in ligands.

    :param block: mmCIF file block
    :param mono: List of monosaccharides
    :param oligo: List of oligosaccharides
    :return: List of residues that are in close contact
    """

    close_contact_residues = []
    close_contact_oligo_chains = set()  # Chain to be deleted from ligands

    close_contact = block.find(
        "_pdbx_validate_close_contact.",
        [
            "auth_comp_id_1",
            "auth_asym_id_2",
            "auth_comp_id_2",
            "auth_seq_id_2",
        ]
    )
    for row in close_contact:
        if row[0].capitalize() in AMINO_ACIDS and row[2] in SUGAR_NAMES:
            res = {"name": row[2], "num": row[3], "chain": row[1]}
            # one residue can be listed more than once in case more than one atom from it
            # is in the close proximity of some atom from AA. Since it is not possible to create a set
            # of dictionaries, it is nessessary to check if there already is the residue.
            if res in mono and res not in close_contact_residues:
                close_contact_residues.append(res)
                mono.remove(res)
            elif res in oligo:
                # Save the chain to remove the whole oligosaccharide
                close_contact_oligo_chains.add(res["chain"])

    for i in range(len(oligo) - 1, -1, -1):
        if oligo[i]["chain"] in close_contact_oligo_chains:
            close_contact_residues.append(oligo[i])
            del oligo[i]

    return close_contact_residues


def save_category(category: Union[Dict, List, Set], filename: str) -> None:
    """
    Save sugars after categorization into JSON files

    :param category: Sugar category to be saved
    :param filename: Name of the JSON file
    """
    with open((config.categorization_dir / f"{filename}.json"), "w", encoding="utf8") as f:
        json.dump(category, f, indent=4)

def count_num_residues(res_in_whole_struct: Dict):
    return sum([len(residues) for residues in res_in_whole_struct.values()])


#TODO: refactor global variable
def categorize(config: Config) -> None:
    # Tmp # FIXME:
    config.categorization_dir.mkdir(exist_ok=True, parents=True)

    global SUGAR_NAMES
    with (config.run_data_dir / "sugar_names.json").open() as f: 
        SUGAR_NAMES = json.load(f)

    logger.info(config.run_data_dir)
    with (config.run_data_dir / "pdb_ids_intersection_pq_ccd.json").open() as f:
        pdb_files = json.load(f)

    for pdb in pdb_files:
        monosacharides = []
        oligosacharides = []

        doc = gemmi.cif.read(str(config.mmcif_files_dir / f"{pdb}.cif"))
        block = doc.sole_block()
        entities: List[str] = list(block.find_values("_entity.type"))
        if "branched" in entities:
            oligo_table = block.find("_pdbx_branch_scheme.", ["pdb_mon_id", "pdb_seq_num", "pdb_asym_id"])
            oligosacharides = extract_sugars(oligo_table)

        if "non-polymer" in entities:
            mono_table = block.find("_pdbx_nonpoly_scheme.", ["pdb_mon_id", "pdb_seq_num", "pdb_strand_id"])
            monosacharides = extract_sugars(mono_table)

        current_all_residues = oligosacharides.copy()
        current_all_residues.extend(monosacharides)

        # If no sugar residues were found, skip to the next structure
        if not current_all_residues:
            pdb_sugars_in_wrong_category.add(block.name)
            continue

        all_residues[block.name] = current_all_residues


        # Remove glycosylations and close contacts from mono and oligosaccharides.
        # Dictionaries are modified in place.
        current_glycosylated = remove_connections(block, monosacharides, oligosacharides)
        current_close_contacts = remove_close_contacts(block, monosacharides, oligosacharides)

        # What is left in mono and oligosaccharides are only ligands
        current_ligands = monosacharides.copy()
        current_ligands.extend(oligosacharides)

        # TODO: Extract to function
        # Store residues from the current structure to the appropirate groups
        if current_ligands:
            ligands[block.name] = current_ligands
        if current_glycosylated:
            glycosylated[block.name] = current_glycosylated
        if current_close_contacts:
            close_contacts[block.name] = current_close_contacts

        if current_ligands and not current_glycosylated and not current_close_contacts:
            pdb_only_ligands.append(block.name)
        if current_glycosylated and not current_ligands and not current_close_contacts:
            pdb_only_glycosylated.append(block.name)
        if current_close_contacts and not current_ligands and not current_glycosylated:
            pdb_only_close_contacts.append(block.name)

        if current_ligands and current_glycosylated and not current_close_contacts:
            pdb_ligand_glycosylated.append(block.name)
        if current_glycosylated and current_close_contacts and not current_ligands:
            pdb_glycosylated_close_contacts.append(block.name)
        if current_close_contacts and current_ligands and not current_glycosylated:
            pdb_ligand_close_contacts.append(block.name)
        if current_ligands and current_glycosylated and current_close_contacts:
            pdb_lig_glyc_close.append(block.name)

    # Save everything
    save_category(ligands, "ligands")
    save_category(glycosylated, "glycosylated")
    save_category(close_contacts, "close_contacts")
    save_category(all_residues, "all_residues")
    save_category(pdb_only_ligands, "pdb_only_ligands")
    save_category(pdb_only_glycosylated, "pdb_only_glycosylated")
    save_category(pdb_only_close_contacts, "pdb_only_close_contacts")
    save_category(pdb_ligand_glycosylated, "pdb_ligand_glycosylated")
    save_category(pdb_ligand_close_contacts, "pdb_ligand_close_contacts")
    save_category(pdb_glycosylated_close_contacts, "pdb_glycosylated_close_contacts")
    save_category(pdb_lig_glyc_close, "pdb_lig_glyc_close")
    save_category(pdb_sugars_in_wrong_category, "pdb_sugars_in_wrong_category")
    save_category(pdb_not_anotated_glycosylation, "pdb_not_anotated_glycosylation")

    # TODO: Extract to function, print into file?
    # Print counts of everything
    logger.info(f"Number of residues with multiple conformations: {len(overall_conformers)}")
    logger.info(f"PDB with unannotated glycosylation: {len(pdb_not_anotated_glycosylation)}")
    logger.info(f"PDB with sugars in the wrong category: {len(pdb_sugars_in_wrong_category)}")

    logger.info(f"All structures: {len(all_residues)}, residues: {count_num_residues(all_residues)}")

    logger.info(f"Ligands: {len(ligands)}, residues: {count_num_residues(ligands)}")

    logger.info(f"Glycosylations: {len(glycosylated)}, residues: {count_num_residues(glycosylated)}")

    logger.info(f"Close contacts: {len(set(close_contacts))}, residues: {count_num_residues(close_contacts)}")

    logger.info(f"PDB only ligands: {len(set(pdb_only_ligands))}")
    logger.info(f"PDB only glycosylated: {len(set(pdb_only_glycosylated))}")
    logger.info(f"PDB only close contacts: {len(set(pdb_only_close_contacts))}")

    logger.info(f"PDB ligands and glycosylated: {len(set(pdb_ligand_glycosylated))}")
    logger.info(f"PDB ligands and close contacts: {len(set(pdb_ligand_close_contacts))}")
    logger.info(f"PDB glycosylated and close contacts: {len(set(pdb_glycosylated_close_contacts))}")
    logger.info(f"PDB ligands, glycosylated and close contacts: {len(set(pdb_lig_glyc_close))}")


    logger.info(f"res_gycosyl_residue_not_1 list: {len(res_gycosyl_residue_not_1)}")
    logger.info(f"res_gycosyl_residue_not_1 set: {len(set(res_gycosyl_residue_not_1))}")


if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)

    # config.categorization_dir.mkdir(exist_ok=True, parents=True)

    categorize(config)
