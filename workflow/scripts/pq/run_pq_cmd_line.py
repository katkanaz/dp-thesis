from argparse import ArgumentParser
import json
import shutil
from subprocess import Popen, PIPE
from pathlib import Path
from platform import system
from datetime import datetime
from typing import List


result_folder_not_created = []

def create_pq_config(structure, residues, sugar: str, run_dir: Path) -> List:
    # print("Creating config file")

    pq_config = {
        "InputFolders": [
            str(run_dir / "structures"),
        ],
        "Queries": [],
        "StatisticsOnly": False,
        "MaxParallelism": 2
    }

    query_names = []

    case_sensitive_check = []
    for residue in residues:
        # print(residue)
        if residue["name"] == sugar:
            case = f"{residue['num']}_{residue['chain']}"
            if case.upper() in case_sensitive_check or case.lower() in case_sensitive_check:
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}_2"
            else:
                case_sensitive_check.append(case)
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}"
            # print(query_id)
            query_names.append(query_id)
            query_str = f"ResidueIds('{residue['num']} {residue['chain']}').AmbientResidues(5)"
            # print(query_str)
            pq_config["Queries"].append({"Id": query_id, "QueryString": query_str})

    if query_names:
        with open(run_dir / "pq_config.json", "w") as f:
            json.dump(pq_config, f, indent=4)

    return query_names


def run_pq(sugar: str, is_unix: bool, run_dir: Path, input_structures: Path, path_to_json: Path) -> None:
    (run_dir / "structures").mkdir(exist_ok=True, parents=True)
    (run_dir / "results").mkdir(exist_ok=True, parents=True)

    with open(path_to_json / "test_modified_ligands.json", "r") as f:
        ligands: dict = json.load(f)


    for structure, residues in ligands.items():
        prefix, pdb_id = structure.split("_", 1)
        structure = f"{prefix}_{pdb_id.lower()}"
        # print(structure)
        # print(residues)
        query_names = create_pq_config(structure, residues, sugar, run_dir)
        # print(query_names)
        if not query_names:
            continue
        for file in sorted(input_structures.glob("*.cif")):
            # print(file.stem)
            if structure in file.name:

                src = file
                dst = run_dir / "structures" / file.name
                shutil.copyfile(src, dst)

                cmd = [f"{'mono ' if is_unix is True else ''}"
                       "../../pq/PatternQuery/WebChemistry.Queries.Service.exe "
                       f"{run_dir}/results "
                       f"{run_dir}/pq_config.json"]


                with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as pq_proc:
                    assert pq_proc.stdout is not None, "stdout is set to PIPE in Popen" 
                    for line in pq_proc.stdout:
                        print(f"STDOUT: {line.strip()}")
                    assert pq_proc.stderr is not None, "stderr is set to PIPE in Popen" 
                    for line in pq_proc.stderr:
                        print(f"STDERR: {line.strip()}")

                if pq_proc.returncode != 0:
                    print(f"PQ process exited with code {pq_proc.returncode}")
                else:
                    print("PQ process completed successfully")

                zip_result_folder = run_dir / "results" / "result/result.zip"
                if not zip_result_folder.exists():
                    result_folder_not_created.append(structure)
                    # Delete the current structure from ./structures directory and continue to the next structure
                    Path(run_dir / "structures" / file.name).unlink()
                    continue

                (run_dir / "structures" / f"{structure}.cif").unlink()
                shutil.rmtree(run_dir / "results" / "result")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)

    args = parser.parse_args()

    is_unix = system() != "Windows"

    run_dir = Path(f"../../debug/pq_altlocs/pq_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}")
    run_dir.mkdir(exist_ok=True, parents=True)

