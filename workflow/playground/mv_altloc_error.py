from enum import Enum
import json
import gemmi
from pathlib import Path
from typing import List, Dict, Set, Tuple


class AltlocCase(Enum):
    SINGLE_RES = 1
    DOUBLE_RES = 2

class AltlocError(Exception):
    def __init__(self, filename, altloc, message="Not supported altloc type") -> None:
        self.filename = filename
        self.altloc = altloc
        self.message = message
        super().__init__(f"{message} {altloc} in file {filename}")

    def __str__(self) -> str:
        return f"{self.message} of {self.altloc} in file: {self.filename}"

class AltlocKind(Enum):
    NO_ALTLOC = 1 # Files with no alternative conformations
    NORMAL_ALTLOC = 2 # Files with both A and B altlocs 
    SINGLE_KIND_ALTLOC = 3 # Files with only A or B altlocs


def save_metadata(input_structure: Path):
    # Load as structure and as file
    doc = gemmi.cif.read(str(input_structure))
    # original_block = original_doc.sole_block()
    structure = gemmi.read_structure(str(input_structure))
    #
    #
    for model_idx, model in enumerate(structure):
        for chain_idx, chain in enumerate(model):
                for residue_idx, residue in enumerate(chain):
                    if residue.name == "GLC":
                        del structure[model_idx][chain_idx][residue_idx]


    # modified_block = structure.make_mmcif_block()
    #
    # new_atom_site = modified_block.find(['_atom_site.'])
    # # new_atom_site_category = modified_block.find_mmcif_category('_atom_site.')
    # new_atom_site_loop = modified_block.find_loop('_atom_site.')
    #
    #
    # # if original_block.find_mmcif_category('_atom_site') is not None:
    # #     original_block.remove_mmcif_category('_atom_site')
    #
    # # Add the new _atom_site category to the original block
    # original_block.set_mmcif_category('_atom_site', atom_site_dict)
    #
    # original_block.init_mmcif_loop(new_atom_site_loop)

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    new_path = Path("/home/kaci/dp/debug/mv_altlocs/2y9g_metadata.cif")
    # structure.make_mmcif_document().write_file(str(new_path), options)
    # new_doc.write_file(str(new_path), options)

def gemmi_test(input_structure: Path, output_path: Path) -> None:
    structure = gemmi.read_structure(str(input_structure), format=gemmi.CoorFormat.Mmcif)
    structure.setup_entities()
    
    for model_idx, model in enumerate(structure):
        for chain_idx, chain in enumerate(model):
                for residue_idx, residue in enumerate(reversed(chain)):
                    if residue.name == "GLC":
                        del structure[model_idx][chain_idx][residue_idx]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    structure.make_mmcif_document().write_file(str(output_path), options)

def test(input_structure: Path, output_path: Path) -> None:
    # structure = gemmi.make_structure_from_block(cif_block)
    structure = gemmi.read_structure(str(input_structure))

    structure.setup_entities()

    to_remove = []

    for model_idx, model in enumerate(structure):
        for chain_idx, chain in enumerate(model):
                for residue_idx, residue in enumerate(chain):
                    if residue.name == "GLC":
                        to_remove.append([model_idx,chain_idx,residue_idx])

    for rm in reversed(to_remove):
        del structure[rm[0]][rm[1]][rm[2]]


    # structure.make_mmcif_headers()
    # structure.make_mmcif_block(gemmi.MmcifOutputGroups(True, atoms=False))

    # groups = gemmi.MmcifOutputGroups(False)
    # groups.ncs = True
    # groups.atoms = True
    # groups.entry = True

    # structure_block = structure.make_mmcif_block()
    # cif_block.update_mmcif_block(structure_block)

    # doc = gemmi.cif.read(str(input_structure))

    # block = doc.find_block((structure.info["_entity.src_method"]))
    # block = doc.find_block("2Y9G")
    # entity_loop = block.find_loop('_entity.id')

    # for row in entity_loop:
    #     print(row)
    # print(entity_loop.tag)
    # structure.update_mmcif_block(block)

    # print(block)
    # for row in block:
    #     print(row)
    groups = gemmi.MmcifOutputGroups(True)
    # groups.ncs = False
    groups.atoms = True

    doc = gemmi.cif.read(str(input_structure))

    # block = doc.sole_block()
    block = doc.find_block(structure.info["_entry.id"])
    structure.update_mmcif_block(block, groups)

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    # doc.write_file(str(new_path), options)

    # structure.make_mmcif_document().write_file(str(output_path), options)
    doc.write_file(str(output_path), options)


def delete_alternative_conformations(structure: gemmi.Structure, residues_to_keep: List[Dict], residues_to_delete: List[Dict], ligand_values: List[Tuple[str, str, str]]) -> List[Dict]:
    """
    Delete unwanted alternative conformations of a structure and set the ones that should be kept to "\0"

    :param structure: Structure in question
    :param residues_to_keep: List of residues whose altlocs should be set to "\0"
    :param residues_to_delete: List of residues to delete in the given structure
    """

    for residue in residues_to_keep:
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        for atom in structure[model_idx][chain_idx][residue_idx]:
            atom.altloc = "\0"


    new_values: Set[Tuple[str, str, str]] = set(ligand_values)
    if len(new_values) != len(ligand_values):
        print(f"Ligand values contains duplicates {new_values=} {ligand_values=}")
    for residue in reversed(residues_to_delete):
        model_idx = residue["model_idx"]
        chain_idx = residue["chain_idx"] 
        residue_idx = residue["residue_idx"]
        if residue["altloc_case"] == AltlocCase.DOUBLE_RES:
            del structure[model_idx][chain_idx][residue_idx]
            res_tuple = (residue["residue_name"], residue["residue_num"], residue["residue_chain"])
            if res_tuple in new_values:
                new_values.remove(res_tuple)
            else:
                print(f"res_str {res_tuple} not in new_values")
        elif residue["altloc_case"] == AltlocCase.SINGLE_RES:
            for atom_idx in reversed(residue["atom_altloc_del"]):
                del structure[model_idx][chain_idx][residue_idx][atom_idx]


    return [{"name": t[0], "num": t[1], "chain": t[2]} for t in new_values]


def save_files(original_file, structure: gemmi.Structure, input_file: Path, conformation_type: str) -> None:
    """
    Save new structure with no sugar altlocs to file

    :param structure: Structure to be saved
    :param input_file: Path to the original file
    :param conformation_type: Type of conformation A or B
    """
    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    new_path = Path("/home/kaci/dp/debug/mv_altlocs/all_altlocs_for_mv/") / f"{conformation_type}_{input_file.name}"
    structure.make_mmcif_document().write_file(str(new_path), options)
    # new_file = structure.make_mmcif_document()
    # structure_block = new_file.sole_block()
    #
    # final_doc = gemmi.cif.Document()
    # block = final_doc.add_new_block(structure_block.name)

    # for item in structure_block:
    #         block.add_copied_item(item)
    #
    # for block in original_file:
    #     if block.name != structure_block.name:
    #         final_doc.add_new_block(block)

# TODO: Add docs
def separate_alternative_conformations(input_file: Path, ligands: Tuple[str, List[Dict]]) -> Tuple[AltlocKind, Dict[str, List[Dict]]]:
    print(f"Processing {input_file.name}")
    with open("/home/kaci/dp/scripts/alternative_conformations/" + "sugar_names.json") as f:
        sugar_names = set(json.load(f)) # Set for optimalization

    global files_support_altloc
    global files_unsupport_altloc
    global files_single_conform_only

    structure_a = gemmi.read_structure(str(input_file))
    original_doc = gemmi.cif.read(str(input_file))
    # structure_a.setup_entities() # FIXME:

    # Lists of alternative conformations
    altloc_a: List[Dict] = []
    altloc_b: List[Dict] = []

    models_count = 0
    for model_idx, model in enumerate(structure_a):
        models_count += 1
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                if residue.name in sugar_names:
                    atom_altloc_a = []
                    atom_altloc_b = []

                    # TODO: decide if keep
                    # NOTE: Can one be sure, one atom won't have a altloc missing
                    # if residue[0].altloc == "\0":
                    #     continue

                    for atom_idx, atom in enumerate(residue):
                        if atom.altloc != "\0":
                            if atom.altloc == "A":
                                atom_altloc_a.append(atom_idx)
                            elif atom.altloc == "B":
                                atom_altloc_b.append(atom_idx)
                            else:
                                raise AltlocError(input_file.name, atom.altloc)

                    if not atom_altloc_a and not atom_altloc_b:
                        # Both lists are empty, residue has no alternate conformations
                        continue

                    common_values = {
                        "model_idx": model_idx,
                        "chain_idx": chain_idx,
                        "residue_idx": residue_idx,
                        "residue_name": residue.name,
                        "residue_num": str(residue.seqid.num),
                        "residue_chain": chain.name
                    }

                    if atom_altloc_a and atom_altloc_b:
                        print(input_file.name)
                        if len(atom_altloc_a) != len(atom_altloc_b):
                            print(f"Not the same number of atoms in each conformation: {input_file.name}")
                        altloc_case = AltlocCase.SINGLE_RES
                        res_a = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_a}
                        altloc_a.append(res_a)
                        res_b = {**common_values, "altloc_case": altloc_case, "atom_altloc_del": atom_altloc_b}
                        altloc_b.append(res_b)
                    elif atom_altloc_a or atom_altloc_b:
                        altloc_case = AltlocCase.DOUBLE_RES
                        res = {**common_values, "altloc_case": altloc_case}
                        list_to_append_to = altloc_a if atom_altloc_a else altloc_b
                        list_to_append_to.append(res)


    # if models_count > 1:
        # print(f"More than one model in: {input_file.name}") #NOTE: Learn if normal

    new_dict = {}
    old_key = ligands[0]

    if not altloc_a and not altloc_b:
        return AltlocKind.NO_ALTLOC, {f"0_{old_key}": ligands[1]}

    single_altloc_kind = bool(altloc_a) != bool(altloc_b)

    ligand_values: List[Tuple[str, str, str]] = [(residue["name"], residue["num"], residue["chain"]) for residue in ligands[1]] 

    if altloc_a:
        # File with only A conformers
        new_values = delete_alternative_conformations(structure_a, altloc_a, altloc_b, ligand_values)
        new_dict[f"A_{old_key}"] = new_values
        save_files(original_doc, structure_a, input_file, "A")

    if altloc_b:
        # File with only B conformers
        structure_b = gemmi.read_structure(str(input_file))
        # structure_b.setup_entities() # FIXME:
        new_values = delete_alternative_conformations(structure_b, altloc_b, altloc_a, ligand_values)
        new_dict[f"B_{old_key}"] = new_values
        save_files(original_doc, structure_b, input_file, "B")

    return AltlocKind.NORMAL_ALTLOC if not single_altloc_kind else AltlocKind.SINGLE_KIND_ALTLOC, new_dict     


def create_separate_mmcifs() -> None:

    with open("/home/kaci/dp/results/ligand_sort/july_2024/" + "categorization/ligands.json", "r") as f:
        ligands: Dict[str, List[Dict]] = json.load(f)

    unsupported_altloc = 0
    supported_altloc = 0
    one_altloc_kind = 0

    ids = [id.lower() for id in ligands.keys()]
    modified_ligands: Dict[str, List[Dict]] = {}
    for file in sorted(Path("/home/kaci/dp/data/july_2024/" + "mmcif_files").glob("*.cif")):
        if file.stem in ids:
            try:
                # NOTE: Might need deepcopy, value is object reference
                altloc_kind, new_ligands = separate_alternative_conformations(file, (file.stem.upper(), ligands[file.stem.upper()]))
                modified_ligands.update(new_ligands)
                if altloc_kind == AltlocKind.NO_ALTLOC:
                    # copy2(file, config.modified_mmcif_files_dir / f"0_{file.name}")
                    pass
                elif altloc_kind == AltlocKind.NORMAL_ALTLOC:
                    supported_altloc += 1
                elif altloc_kind == AltlocKind.SINGLE_KIND_ALTLOC:
                    supported_altloc += 1
                    one_altloc_kind += 1
                
            except AltlocError as e:
                unsupported_altloc += 1
                print(f"Exception caught: {e}")

    with open("/home/kaci/dp/debug/mv_altlocs/test_modifiend_ligands.json", "w", encoding="utf8") as f:
        json.dump(modified_ligands, f, indent=4)

    print(f"Number of files with supported altlocs: {supported_altloc}")
    print(f"Number of files with unsupported altlocs: {unsupported_altloc}")
    print(f"Number of files with just one altloc kind: {one_altloc_kind}")
    

import gemmi
from pathlib import Path

def write_structure(input_structure: Path, output_path: Path) -> None:
    structure = gemmi.read_structure(str(input_structure))
    structure.setup_entities()

    to_remove = []
    
    for model_idx, model in enumerate(structure):
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                # simplified example of removing residues/atoms
                # in my code I filter by altloc value on the level of atoms
                if residue.name == "GLC":
                    to_remove.append([model_idx,chain_idx,residue_idx])

    for rm in reversed(to_remove):
        del structure[rm[0]][rm[1]][rm[2]]

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    structure.make_mmcif_document(gemmi.MmcifOutputGroups(True, chem_comp=False, entity=False)).write_file(str(output_path), options)


# NOTE: Works best so far
def write_doc(input_structure: Path, output_path: Path) -> None:
    structure = gemmi.read_structure(str(input_structure))
    structure.setup_entities()

    to_remove = []

    for model_idx, model in enumerate(structure):
        for chain_idx, chain in enumerate(model):
            for residue_idx, residue in enumerate(chain):
                # simplified example of removing residues/atoms
                # in my code I filter by altloc value on the level of atoms
                if residue.name == "GLC":
                    to_remove.append([model_idx,chain_idx,residue_idx])

    for rm in reversed(to_remove):
        del structure[rm[0]][rm[1]][rm[2]]


    groups = gemmi.MmcifOutputGroups(True, chem_comp=False, entity=False, auth_all=True)
    groups.atoms = True

    doc = gemmi.cif.read(str(input_structure))

    # block = doc.find_block(structure.info["_entry.id"])
    block = doc.sole_block()
    structure.update_mmcif_block(block, groups)

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    doc.write_file(str(output_path), options)


def read_write_doc(input_path: Path, output_path: Path) -> None:
    doc = gemmi.cif.read_file(str(input_path))

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    doc.write_file(str(output_path), options)


def del_atloc_from_doc(input_file: Path, output_file: Path) -> None:
    doc = gemmi.cif.read_file(str(input_file))
    block = doc.sole_block()
    atom_site = block.find_loop("_atom_site")
    print(atom_site)

    options = gemmi.cif.WriteOptions()
    options.misuse_hash = True
    options.align_pairs = 48
    options.align_loops = 20

    doc.write_file(str(output_file), options)


if __name__ == "__main__":
    # gemmi_test(Path("/home/kaci/dp/debug/mv_altlocs/2y9g.cif"), Path("/home/kaci/dp/debug/mv_altlocs/2y9g_just_struc.cif"))
    # test(Path("/home/kaci/dp/debug/mv_altlocs/2y9g.cif"), Path("/home/kaci/dp/debug/mv_altlocs/2y9g_test_17.cif"))
    # create_separate_mmcifs()

    # write_structure(Path("/home/kaci/dp/debug/mv_altlocs/gemmi_advice/2y9g.cif"),
    #                 Path("/home/kaci/dp/debug/mv_altlocs/gemmi_advice/2y9g_struc_1.cif"))
    write_doc(Path("/home/kaci/dp/debug/mv_altlocs/gemmi_advice/2y9g.cif"),
              Path("/home/kaci/dp/debug/mv_altlocs/gemmi_advice/2y9g_doc_2.cif"))
    # read_write_doc(Path("/home/kaci/dp/debug/mv_altlocs/read_write_test/2y9g.cif"),
    #                 Path("/home/kaci/dp/debug/mv_altlocs/read_write_test/2y9g_just_write_1.cif"))
    # del_atloc_from_doc(Path("/home/kaci/dp/debug/mv_altlocs/del_altloc_from_doc/2y9g.cif"),
    #                 Path("/home/kaci/dp/debug/mv_altlocs/del_altloc_from_doc/2y9g_test_2.cif"))
