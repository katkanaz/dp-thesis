import json
from pathlib import Path
from pydantic import BaseModel
from typing import Union

class Config(BaseModel):
    data_dir: Path
    results_dir: Path
    images_dir: Path
    mv_dir: Path
    pq_dir: Path

    sugar_binding_patterns_dir: Path
    components_dir: Path
    mmcif_files_dir: Path
    no_o6_mmcif_dir: Path
    validation_files_dir: Path
    sugars_dir: Path
    categorization_dir: Path
    validation_dir: Path
    mv_run_dir: Path
    graph_analysis_dir: Path
    residue_graphs_dir: Path
    pq_run_dir: Path
    raw_binding_sites_dir: Path
    filtered_binding_sites_dir: Path
    clusters_dir: Path
    structure_motif_search_dir: Path
    dendrograms_dir: Path
    tanglegrams_dir: Path
    @classmethod
    def load(cls, file_path: Union[Path, str], sugar: str, current_run: str, data_run: str) -> "Config":
        with open(file_path, "r") as f:
            data = json.load(f)
        config = cls(**data)
        config._update_relative_paths(sugar, current_run, data_run)

        return config
