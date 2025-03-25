from pathlib import Path
from pymol import cmd
from typing import Tuple, List
import math


def select_sugar(filename: str) -> str:
    try:
        _, _, res, num, chain = filename.split("_")
    except ValueError:
        _, _, res, num, chain, _ = filename.split("_")

    if len(chain) > 1:
        chain = chain[0]

    sugar = f"/{filename}//{chain}/{res}`{num}"
    cmd.select("sugar", sugar)

    return sugar


def get_sugar_ring_center(sugar: str) -> List[float]:
    # ring_atoms = "name C1+C2+C3+C4+C5+O4"
    # selection = f"{sugar} and ({ring_atoms})"
    #
    # if cmd.count_atoms(selection) == 0:
    #     raise ValueError("No sugar ring atoms found! Check atom names or sugar selection.")

    return cmd.centerofmass(sugar)


def measure_distances(residues: List[Tuple[str, str]], sugar_center) -> List[Tuple[Tuple[str, str], float]]:
    distances: List[Tuple[Tuple[str, str], float]] = []

    cmd.pseudoatom(object="tmp", pos=sugar_center)
    for resi, resn in residues:
        # current_residue = f"resi {resi} and name CA"
        # sugar_atom = "sugar and name C1"
        atoms = cmd.get_model(f"resi {resi}").atom
        min_distance = math.inf
        
        # distance_value: float = cmd.get_distance(current_residue, sugar_atom) # In Angstroms [Å]
        for atom in atoms:
            distance = cmd.get_distance(f"resi {resi} and index {atom.index}", "tmp") # In Angstroms [Å]
            if distance < min_distance:
                min_distance = distance

        distances.append(((resn, resi), min_distance))
        # distances.append(((resn, resi), distance_value))

    print(distances)
    return distances


def sort_distances(distances: List[Tuple[Tuple[str, str], float]], max_res: int) -> List[Tuple[Tuple[str, str], float]]:
    sorted_distances = sorted(distances, key=lambda item: item[1])
    
    return sorted_distances[max_res:]


def remove_residues(residues_to_remove: List[Tuple[Tuple[str, str], float]]) -> None:
    for (_, resi), _ in residues_to_remove:
        cmd.remove(f"resi {resi}")
        

def foo(max_res: int, path_to_file: Path):
    cmd.delete("all")
    cmd.load(path_to_file)
    count = cmd.count_atoms("n. CA and polymer")
    print(f"File {path_to_file.name}: {count} residues")

    filename = Path(path_to_file.name).stem

    sugar = select_sugar(filename)
    sugar_center = get_sugar_ring_center(sugar)
    # print(sugar_center)
    

    if count > max_res:
        residues: List[Tuple[str, str]] = []
        cmd.iterate("n. CA and polymer", "residues.append((resi, resn))",
                    space=locals())
        
        distances = measure_distances(residues, sugar_center)

        residues_to_remove = sort_distances(distances, max_res)
        remove_residues(residues_to_remove)

        cmd.save(f"/home/kaci/dp/tmp/pymol_test/max_10_res/{filename}.pdb")

def test(path_to_file: Path):
    cmd.delete("all")
    cmd.load(path_to_file)
    count = cmd.count_atoms("n. CA and polymer")
    print(f"File {path_to_file.name}: {count} residues")


if __name__ == "__main__":
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/2_4d4u_FUC_3_C.pdb"))
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/51_1cr7_GAL_2_K.pdb"))
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/63_3zzv_FUC_3_E.pdb"))
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/103_3uet_FUC_3_C.pdb"))
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/15_6t9a_FUC_101_A.pdb"))
    # test(Path("/home/kaci/dp/tmp/pymol_test/max_10_res/19_1gzt_FUC_201_A.pdb"))
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/3_7khu_FUC_5_E.pdb"))
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/4_4d4u_FUC_2_J.pdb"))
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/5_4d4u_FUC_3_H.pdb"))
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/6_4d4u_FUC_4_I.pdb"))
    # foo(10, Path("/home/kaci/dp/tmp/pymol_test/7_4d4u_FUC_4_E.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/1_1rk2_RIB_311_D.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/63_3zzv_FUC_3_E.pdb"))
