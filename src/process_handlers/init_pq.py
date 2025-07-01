"""
Script Name: init.py
Description: Run PatternQuery to obtain PDB IDs of structures with sugars
Authors: Kateřina Nazarčuková
"""


import json
from platform import system
from subprocess import Popen, PIPE

from logger import logger, setup_logger

from configuration import Config


# FIXME: Put download PQ here!

def create_config(config: Config) -> None:
    pq_config = {
        "InputFolders": [
            str(), # FIXME: Here goes pdb mirror
        ],
        "Queries": [
            {
                # FIXME: Sugar pattern
                "Id": "Structures with sugars",
                "QueryString": """Or(
                                    AtomNames('C3').Inside(Rings(4*['C']+['O'])),
                                    AtomNames('C4').Inside(Rings(4*['C']+['O'])),
                                    AtomNames('C3').Inside(Rings(5*['C']+['O'])),
                                    AtomNames('C4').Inside(Rings(5*['C']+['O']))
                                ).Filter(lambda a:a.IsConnectedTo(Atoms('O')))"""
            }
        ],
        "StatisticsOnly": False,
        "MaxParallelism": 2
    }

    with open(config.init_pq / "config.json", "w") as f: # FIXME: Update configuration for this
        json.dump(pq_config, f, indent=4)

def run_init_pq(config: Config, is_unix: bool) -> None:
    cmd = [f"{'mono ' if is_unix is True else ''}"
           f"{config.user_cfg.pq_dir}/PatternQuery/WebChemistry.Queries.Service.exe "
           f"{config.init_pq}/results "
           f"{config.init_pq}/pq_config.json"]

    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as pq_proc:
        assert pq_proc.stdout is not None, "stdout is set to PIPE in Popen" 
        for line in pq_proc.stdout:
            logger.info(f"STDOUT: {line.strip()}")
        assert pq_proc.stderr is not None, "stderr is set to PIPE in Popen" 
        for line in pq_proc.stderr:
            logger.error(f"STDERR: {line.strip()}")

    if pq_proc.returncode != 0:
        logger.error(f"PQ process exited with code {pq_proc.returncode}")
    else:
        logger.info("PQ process completed successfully")


if __name__ == "__main__":
    config = Config.load("config.json", None, True)

    setup_logger(config.log_path)

    is_unix = system() != "Windows"

    run_init_pq(config, is_unix)
