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

def delete_alternate_conformations():
    pass
    current_run = Config.get_current_run()
    config = Config.load("config.json", None, current_run, None)

    setup_logger(config.log_path)
    
    separate_alternate_conformations()
