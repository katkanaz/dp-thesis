"""
Script Name: categorize.py
Description: Categorize sugar residues from all structures to separate the lignads.
Authors: Daniela Repelová, Kateřina Nazarčuková
Credits: Original concept by Daniela Repelová, modifications by Kateřina Nazarčuková
"""


import json

import gemmi
from gemmi.cif import Block  # type: ignore

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

#TODO: add type hints
def extract_sugars(table):
    #TODO: add docs
    """
    Gets a list of dictionaries, in which one dictionary represents single
    sugar residue present in the given table (either monosacharide or one
    residue form oligosaccharide).
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


def remove_connections(block: Block, mono: list, oligo: list) -> list:
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


def remove_close_contacts(block: Block, mono: list, oligo: list) -> list:
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
    close_contact_oligo_chains = set()  # chain to be deleted from ligands

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
                # save the chain to remove the whole oligosaccharide
                close_contact_oligo_chains.add(res["chain"])

    for i in range(len(oligo) - 1, -1, -1):
        if oligo[i]["chain"] in close_contact_oligo_chains:
            close_contact_residues.append(oligo[i])
            del oligo[i]

    return close_contact_residues

#TODO: refactor global variable
def categorize(config: Config):
    global SUGAR_NAMES
    with (config.data_folder / "sugar_names.json").open() as f: 
        SUGAR_NAMES = json.load(f)

    with (config.data_folder / "pdb_ids_intersection_pq_ccd.json").open() as f:
        pdb_files = json.load(f)

    for pdb in pdb_files:
        monosacharides = []
        oligosacharides = []

        doc = gemmi.cif.read(str(config.mmcif_files / f"{pdb}.cif"))
        block = doc.sole_block()
        entities = block.find_values("_entity.type")
        entities = [entity for entity in entities]
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


        # Remove glycosylations and close contacts from mono and oligosaccharides. Dictionaries are modified in place.
        current_glycosylated = remove_connections(block, monosacharides, oligosacharides)
        current_close_contacts = remove_close_contacts(block, monosacharides, oligosacharides)

        # What is left in mono and oligosaccharides are only ligands
        current_ligands = monosacharides.copy()
        current_ligands.extend(oligosacharides)

        #TODO: extract to function
        # store residues from the current structure to the appropirate groups
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

    #TODO: extract to function
    # save everything
    with open((config.categorization_results / "ligands.json"), "w") as f:
        json.dump(ligands, f, indent=4)
    with open((config.categorization_results / "glycosylated.json"), "w") as f:
        json.dump(glycosylated, f, indent=4)
    with open((config.categorization_results / "close_contacts.json"), "w") as f:
        json.dump(close_contacts, f, indent=4)

    with open((config.categorization_results / "all_residues.json"), "w") as f:
        json.dump(all_residues, f, indent=4)

    with open((config.categorization_results / "pdb_only_ligands.json"), "w") as f:
        json.dump(pdb_only_ligands, f, indent=4)
    with open((config.categorization_results / "pdb_only_glycosylated.json"), "w") as f:
        json.dump(pdb_only_glycosylated, f, indent=4)
    with open((config.categorization_results / "pdb_only_close_contacts.json"), "w") as f:
        json.dump(pdb_only_close_contacts, f, indent=4)

    with open((config.categorization_results / "pdb_ligand_glycosylated.json"), "w") as f:
        json.dump(pdb_ligand_glycosylated, f, indent=4)
    with open((config.categorization_results / "pdb_ligand_close_contacts.json"), "w") as f:
        json.dump(pdb_ligand_close_contacts, f, indent=4)
    with open((config.categorization_results / "pdb_glycosylated_close_contacts.json"), "w") as f:
        json.dump(pdb_glycosylated_close_contacts, f, indent=4)
    with open((config.categorization_results / "pdb_lig_glyc_close.json"), "w") as f:
        json.dump(pdb_lig_glyc_close, f, indent=4)

    with open((config.categorization_results / "pdb_sugars_wrong_category.json"), "w") as f:
        json.dump(list(pdb_sugars_in_wrong_category), f, indent=4)
    with open((config.categorization_results / "pdb_glycosylation_not_anotated.json"), "w") as f:
        json.dump(list(pdb_not_anotated_glycosylation), f, indent=4)

    #TODO: extract to function, print into file?
    # print counts of everything
    print("Number of residues with multiple conformations: ", len(overall_conformers))
    print("PDB with unannotated glycosylation:", len(pdb_not_anotated_glycosylation))
    print(f"PDB with sugars in the wrong category: {len(pdb_sugars_in_wrong_category)}\n")
    print()

    count = 0
    for residues in all_residues.values():
        count += len(residues)
    print(f"All structures: {len(all_residues)} , residues: {count}\n")

    count = 0
    for residues in ligands.values():
        count += len(residues)
    print(f"Ligands: {len(ligands)} , residues: {count}\n")

    count = 0
    for i in glycosylated.values():
        count += len(i)
    print(f"Glycosylations: {len(glycosylated)} , residues: {count}\n")

    count = 0
    for i in close_contacts.values():
        count += len(i)
    print(f"Close contacts: {len(set(close_contacts))} , residues: {count}\n")

    print(f"PDB only ligands: {len(set(pdb_only_ligands))}\n")
    print(f"PDB only glycosylated: {len(set(pdb_only_glycosylated))}\n")
    print(f"PDB only close contacts: {len(set(pdb_only_close_contacts))}\n")

    print(f"PDB ligands and glycosylated: {len(set(pdb_ligand_glycosylated))}\n")
    print(f"PDB ligands and close contacts: {len(set(pdb_ligand_close_contacts))}\n")
    print(f"PDB glycosylated and close contacts: {len(set(pdb_glycosylated_close_contacts))}\n")
    print(f"PDB ligands, glycosylated and close contacts: {len(set(pdb_lig_glyc_close))}\n")


    print(f"res_gycosyl_residue_not_1 list: {len(res_gycosyl_residue_not_1)}\n")
    print(f"res_gycosyl_residue_not_1 set: {len(set(res_gycosyl_residue_not_1))}\n")




if __name__ == "__main__":
    config = Config.load("config.json")

    config.categorization_results.mkdir(exist_ok=True, parents=True)

    categorize(config)
