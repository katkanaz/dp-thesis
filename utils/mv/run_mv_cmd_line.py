import json
from subprocess import Popen, PIPE
from platform import system
from datetime import datetime
from pathlib import Path


def create_mv_config(run_dir: Path) -> None:
    print("Creating config file")

    mv_config = {
        "ValidationType": "Sugars",
        "InputFolder":  "../../tmp/alter_conform/mv_pq_test_single_conform/",
        "ModelsSource": "../mv/components_sugars_only.cif",
        "IsModelsSourceComponentDictionary": True,
        "IgnoreObsoleteComponentDictionaryEntries": False,
        "SummaryOnly": False,
        "DatabaseModeMinModelAtomCount": 0,
        "DatabaseModeIgnoreNames": [],
        "MaxDegreeOfParallelism": 8
    }

    with open(f"{run_dir}/mv_config.json", "w", encoding="utf8") as f:
        json.dump(mv_config, f, indent=4)
    

def run_mv(is_unix: bool, run_dir: Path) -> None:
    create_mv_config(run_dir)

    cmd = [f"{'mono ' if is_unix is True else ''}"
           "../../mv/MotiveValidator/WebChemistry.MotiveValidator.Service.exe "
           f"{run_dir}/results "
           f"{run_dir}/mv_config.json"]

    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as mv_proc:
        assert mv_proc.stdout is not None, "stdout is set to PIPE in Popen"
        for line in mv_proc.stdout:
            print(f"STDOUT: {line.strip()}")
        assert mv_proc.stderr is not None, "stderr is set to PIPE in Popen"
        for line in mv_proc.stderr:
            print(f"STDERR: {line.strip()}")

    if mv_proc.returncode != 0:
        print(f"MV process exited with code {mv_proc.returncode}")
    else:
        print("MV process completed successfully")

if __name__ == "__main__":
    is_unix = system() != "Windows"
    Path(f"../../tmp/mv_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}").mkdir(exist_ok=True, parents=True)
    run_dir = Path(f"../../tmp/mv_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}")

    run_mv(is_unix, run_dir)
