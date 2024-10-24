import json
from pathlib import Path
from pydantic import BaseModel
from typing import Union

class Config(BaseModel):
    binding_sites: Path
    data_folder: Path
    mmcif_files: Path
    validation_files: Path
    results_folder: Path
    mv_folder: Path
    pq_folder: Path
    dendrograms: Path
    tanglegrams: Path
    categorization_results: Path
    patterns_folder: Path
    validation_results: Path
    removed_o6_folder: Path
    graph_analysis: Path

    @classmethod
    def load(cls, file_path: Union[Path, str]) -> "Config":
        with open(file_path, "r") as f:
            data = json.load(f)
        return  cls(**data)
