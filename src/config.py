import json
from pathlib import Path
from pydantic import Basemodel

class Config(Basemodel):
    data_folder: Path
    results_folder: Path
    mv_working_path: Path
    mv_results: Path
    pq_working_path: Path
    pq_results: Path
    pq_structures: Path
    dendrograms: Path
    tanglegrams: Path

    @classmethod
    def load(cls, file_path: Path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return  cls(**data)