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


    def _update_relative_paths(self, sugar: str, current_run: str, data_run: str):
        if data_run is None:
            data_run = current_run # WARNING: how to deal with this?

        self.sugar_binding_patterns_dir = self.data_dir / f"{current_run}/sugar_binding_patterns"
        self.components_dir = self.data_dir / f"{current_run}/components"
        self.mmcif_files_dir = self.data_dir / f"{data_run}/mmcif_files"
        self.no_o6_mmcif_dir = self.data_dir / f"{current_run}/no_o6_mmcif" # FIXME: chceck if this is first or second run?
        self.validation_files_dir = self.data_dir / f"{current_run}/validation_files"
        self.sugars_dir = self.data_dir / f"{data_run}/sugars" # FIXME: this is from second run, is that problem?
        self.categorization_dir = self.results_dir / f"ligand_sort/{current_run}/categorization"
        self.validation_dir = self.results_dir / f"ligand_sort/{current_run}/validation"
        self.mv_run_dir = self.results_dir / f"ligand_sort/{current_run}/mv_run"
        self.graph_analysis_dir = self.results_dir / f"ligand_sort/{current_run}/graph_analysis"
        self.residue_graphs_dir = self.images_dir / f"ligands/{current_run}/residue_graphs"
        self.pq_run_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/pq_run"
        self.raw_binding_sites_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/raw_binding_sites"
        self.filtered_binding_sites_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/filtered_binding_sites"
        self.clusters_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/clusters"
        self.structure_motif_search_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/structure_motif_search"
        self.dendrograms_dir = self.images_dir / f"binding_sites/{sugar}/{current_run}/dendrograms"
        self.tanglegrams_dir = self.images_dir / f"binding_sites/{sugar}/{current_run}/tanglegrams"

    
