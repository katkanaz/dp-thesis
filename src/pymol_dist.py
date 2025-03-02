from pathlib import Path
from pymol import cmd
from typing import Dict, Tuple, List


def foo(max_res: int, path_to_file: Path):
    cmd.delete("all")
    cmd.load(path_to_file)
    count = cmd.count_atoms("n. CA and polymer")
    print(f"File {path_to_file.name}: {count} residues")

    filename = Path(path_to_file.name).stem

    try:
        _, _, res, num, chain = filename.split("_")
    except ValueError:
        _, _, res, num, chain, _ = filename.split("_")

    if len(chain) > 1:
        chain = chain[0]

    sugar_name = res
    sugar = f"/{filename}//{chain}/{res}`{num}"
    cmd.select("sugar", sugar)
    
    if count > max_res:
        residues: List[Tuple[str, str]] = []
        distances: Dict[Tuple[str, str], float] = {}
        cmd.iterate("n. CA and polymer", "residues.append((resi, resn))",
                    space=locals())
        
        for resi, resn in residues:
            current_residue = f"resi {resi} and name CA"
            # distance_name = f"dist_{resi}"
            sugar_atom = "sugar and name C1"

            # cmd.distance(f"dist_{resi}", current_residue, sugar_atom)
            
            distance_value: float = cmd.get_distance(current_residue, sugar_atom) # In Angstroms [Å]
            # print(type(resi))
            # print(type(resn))
            distances[resn, resi] = distance_value
            # print(type(distance_value))



            # print(f"Distance between residue {resn} ({resi}) and {sugar_name}: {distance_value} Å")
        # print(type(residues))
        # print(distances)
        sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1]))
        print(sorted_distances)

    # return distances



if __name__ == "__main__":
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/15_6t9a_FUC_101_A.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/19_1gzt_FUC_201_A.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/63_3zzv_FUC_3_E.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/103_3uet_FUC_3_C.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/3_1bos_GAL_2_0.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/4_1bos_GAL_2_2.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/51_1cr7_GAL_2_K.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/58_3leg_FUC_4_B.pdb"))
