from pathlib import Path
from pymol import cmd
from typing import Tuple, List
import math


def select_sugar(filename: str) -> Tuple[str, str]:
    try:
        _, _, res, num, chain = filename.split("_")
    except ValueError:
        _, _, res, num, chain, _ = filename.split("_")

    if len(chain) > 1:
        chain = chain[0]

    sugar = f"/{filename}//{chain}/{res}`{num}"
    selection_name = "sugar"
    cmd.select(selection_name, sugar)

    return sugar, selection_name


def get_sugar_ring_center(sugar: str) -> List[float]:
    return cmd.centerofmass(sugar)


def measure_distances(residues: List[Tuple[str, str]], sugar_center, filename) -> List[Tuple[Tuple[str, str], float]]:
    distances: List[Tuple[Tuple[str, str], float]] = []

    cmd.pseudoatom(object="tmp", pos=sugar_center)
    for resi, resn in residues:
        # print(resn)
        atoms = cmd.get_model(f"{filename} and resi {resi}").atom
        min_distance = math.inf
        
        for atom in atoms:
            # selector = f"{filename} and chain {atom.chain} and resi {atom.resi} and name {atom.name} and alt ''"
            # count = cmd.count_atoms(selector)
            # if count != 1:
            #     print(count, selector)
            # print(f"Selector: {selector}, Count: {cmd.count_atoms(selector)}")
            # print(atom.resn)
            # distance = cmd.get_distance(f"resi {resi} and index {atom.index}", "tmp") # In Angstroms [Å]
            distance = cmd.get_distance(f"{filename} and index {atom.index}", "tmp") # In Angstroms [Å]
            # print(distance)
            if distance < min_distance:
                min_distance = distance

        distances.append(((resn, resi), min_distance))

    print(distances)

    cmd.delete("tmp")
    return distances


def sort_distances(distances: List[Tuple[Tuple[str, str], float]], max_res: int) -> List[Tuple[Tuple[str, str], float]]:
    sorted_distances = sorted(distances, key=lambda item: item[1])
    return sorted_distances[max_res:]


def remove_residues(residues_to_remove: List[Tuple[Tuple[str, str], float]]) -> None:
    for (_, resi), _ in residues_to_remove:
        cmd.remove(f"resi {resi}")
        

def modify_pdb(max_res: int, path_to_file: Path):
    cmd.delete("all")
    cmd.load(path_to_file)
    
    print("Objects loaded:", cmd.get_names())
    cmd.select("all")  # Force internal consistency
    print("Atom count:", cmd.count_atoms("all"))

    count = cmd.count_atoms("n. CA and polymer")
    print(f"File {path_to_file.name}: {count} residues")

    filename = Path(path_to_file).stem

    sugar_path, sugar_name = select_sugar(filename)
    sugar_center = get_sugar_ring_center(sugar_name)
    

    if count > max_res:
        residues: List[Tuple[str, str]] = []
        cmd.iterate("n. CA and polymer", "residues.append((resi, resn))",
                    space=locals())
        
        distances = measure_distances(residues, sugar_center, filename)

        residues_to_remove = sort_distances(distances, max_res)
        remove_residues(residues_to_remove)

        cmd.save(f"/home/kaci/dp/tmp/pymol_test/max_10_res/{filename}.pdb")

def test(path_to_file: Path):
    cmd.delete("all")
    cmd.load(path_to_file)
    count = cmd.count_atoms("n. CA and polymer")
    print(f"File {path_to_file.name}: {count} residues")


if __name__ == "__main__":
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/19_1gzt_FUC_201_A.pdb"))
    # modify_pdb(10, Path("/home/kaci/dp/tmp/pymol_dist_test/raw_bs/0_6jk3_FUC_3_F.pdb"))
    # modify_pdb(10, Path("/home/kaci/dp/tmp/pymol_dist_test/raw_bs/0_6fx1_FUC_4_T.pdb"))
    # modify_pdb(10, Path("/home/kaci/dp/tmp/pymol_test/no_mass/0_7c38_FUC_404_A.pdb"))
    modify_pdb(10, Path("/home/kaci/dp/tmp/pymol_test/no_mass/0_7c38_FUC_404_B.pdb"))
