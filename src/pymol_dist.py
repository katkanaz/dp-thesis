from pathlib import Path
from pymol import cmd


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

    sugar = f"/{filename}//{chain}/{res}`{num}"
    cmd.select("sugar", sugar)
    
    if count > max_res:
        distances = []
        cmd.iterate("n. CA and polymer", "distances.append((resi, resn))", space=locals())
        
        for resi, resn in distances:
            current_residue = f"resi {resi} and name CA"
            # distance_name = f"dist_{resi}"
            sugar_atom = "sugar and name C1"

            # cmd.distance(f"dist_{resi}", current_residue, sugar_atom)
            
            distance_value = cmd.get_distance(current_residue, sugar_atom)

            print(f"Distance between residue {resn} ({resi}) and sugar: {distance_value} Å")

    # return distances



if __name__ == "__main__":
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/15_6t9a_FUC_101_A.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/19_1gzt_FUC_201_A.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/63_3zzv_FUC_3_E.pdb"))
    foo(10, Path("/home/kaci/dp/tmp/pymol_test/103_3uet_FUC_3_C.pdb"))
