from argparse import ArgumentParser
import json
from subprocess import Popen, PIPE
from pathlib import Path
from platform import system
from datetime import datetime


def create_pq_config(sugar: str, run_dir: Path) -> None:
    print("Creating config file")

    pq_config = {
        "InputFolders": [
            "../../tmp/alter_conform/mv_pq_test_single_conform",
        ],
        "Queries": [],
        "StatisticsOnly": False,
        "MaxParallelism": 2
    }

    structure = "1d0k"
    residues = [{
                "name": "NAG",
                "num": "2",
                "chain": "B"
            }]

    case_sensitive_check = []
    for residue in residues:
        if residue["name"] == sugar:
            case = f"{residue['num']}_{residue['chain']}"
            if case.upper() in case_sensitive_check or case.lower() in case_sensitive_check:
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}_2"
            else:
                case_sensitive_check.append(case)
                query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}"
            query_str = f"ResidueIds('{residue['num']} {residue['chain']}').AmbientResidues(5)"
            pq_config["Queries"].append({"Id": query_id, "QueryString": query_str})

    with open(f"{run_dir}/pq_config.json", "w") as f:
        json.dump(pq_config, f, indent=4)


def run_pq(sugar: str, is_unix: bool, run_dir: Path) -> None:
    create_pq_config(sugar, run_dir)

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


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)

    args = parser.parse_args()

    is_unix = system() != "Windows"

    run_dir = Path(f"../../tmp/pq_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}")
    Path(f"../../tmp/pq_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}").mkdir(exist_ok=True, parents=True)
    run_pq(args.sugar, is_unix, run_dir)
