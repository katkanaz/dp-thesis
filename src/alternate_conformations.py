"""
Script Name: alternate_conformations.py
Description: Create separate mmCIF files for alternate sugar conformations
Author: Kateřina Nazarčuková
"""


import gemmi
from gemmi.cif import Block  # type: ignore
from pathlib import Path
from typing import List

from logger import logger, setup_logger
from configuration import Config

def load_mmcif(config: Config) -> List[Path]:
    mmcifs = []
    for file in sorted(Path("").glob("*.cif")):
        mmcifs.append(file)
    
    return mmcifs

def delete_alternate_conformations() -> None:
    pass

def separate_alternate_conformations() -> None:
    pass
    

if __name__ == "__main__":
    config = Config.load("config.json", None, False)

    setup_logger(config.log_path)
    
    separate_alternate_conformations()
