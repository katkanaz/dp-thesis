import json
from pathlib import Path
from pydantic import BaseModel
from typing import Union
from datetime import datetime
import os
from logger import logger


class Config(BaseModel):
    data_dir: Path
    results_dir: Path
    images_dir: Path
    mv_dir: Path
    pq_dir: Path

    log_path: Path
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
    def load(cls, file_path: Union[Path, str], sugar: Union[str, None], need_data_run: bool, force_new: bool = False) -> "Config":
        with open(file_path, "r") as f:
            data = json.load(f)
        config = cls(**data)
        current_run = config.get_current_run(force_new)
        data_run = config.get_data_run(config.data_dir) if need_data_run else None
        config._update_relative_paths(sugar, current_run, data_run)

        return config


    def _update_relative_paths(self, sugar: Union[str, None], current_run: str, data_run: Union[str, None]) -> None:
        if data_run is None:
            data_run = current_run

        self.log_path = self.results_dir / f"" # FIXME: how to setup the log? if one where? or 2 for 2 runs?
        self.sugar_binding_patterns_dir = self.data_dir / f"{data_run}/sugar_binding_patterns"
        self.components_dir = self.data_dir / f"{data_run}/components"
        self.mmcif_files_dir = self.data_dir / f"{data_run}/mmcif_files"
        self.no_o6_mmcif_dir = self.data_dir / f"{data_run}/no_o6_mmcif" # FIXME: check if this is first or second run?
        self.validation_files_dir = self.data_dir / f"{data_run}/validation_files"
        self.categorization_dir = self.results_dir / f"ligand_sort/{data_run}/categorization"
        self.validation_dir = self.results_dir / f"ligand_sort/{data_run}/validation"
        self.mv_run_dir = self.results_dir / f"ligand_sort/{data_run}/mv_run"
        self.graph_analysis_dir = self.results_dir / f"ligand_sort/{data_run}/graph_analysis"
        self.residue_graphs_dir = self.images_dir / f"ligands/{data_run}/residue_graphs"

        # Sugars are always newer than the data run, since they are downloaded by the second part of the process
        self.sugars_dir = self.data_dir / f"{data_run}/sugars"

        if sugar is not None:
            self.pq_run_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/pq_run"
            self.raw_binding_sites_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/raw_binding_sites"
            self.filtered_binding_sites_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/filtered_binding_sites"
            self.clusters_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/clusters"
            self.structure_motif_search_dir = self.results_dir / f"motif_based_search/{sugar}/{current_run}/structure_motif_search"
            self.dendrograms_dir = self.images_dir / f"binding_sites/{sugar}/{current_run}/dendrograms"
            self.tanglegrams_dir = self.images_dir / f"binding_sites/{sugar}/{current_run}/tanglegrams"

    
    @classmethod
    def get_data_run(cls, data_dir) -> str:
        newest_directory = None

        for directory_name in os.listdir(data_dir):
            directory_path = os.path.join(data_dir, directory_name)
            if os.path.isdir(directory_path):
                try:
                    datetime.strptime(directory_name, "%Y-%m-%dT%H-%M-%S")
                    if newest_directory is None or directory_name > newest_directory:
                        newest_directory = directory_name
                except ValueError:
                    continue

        assert newest_directory is not None, "Data directory should contain at least one directory from the run of the previous program."
        return newest_directory



    @classmethod
    def get_current_run(cls, force_new: bool = False) -> str:
        file_path = "../.current_run"

        if os.path.isfile(file_path) and not force_new:
            with open(file_path, "r", encoding="utf8") as f:
                current_datetime = f.read()

            return current_datetime
        else:
            current_datetime = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            with open(file_path, "w", encoding="utf8") as f:
                f.write(current_datetime)

            return current_datetime


    @classmethod     
    def clear_current_run(cls) -> None:
        """
        Delete .current_run file from results directory.
        """
        file_path = "../.current_run"
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"File {file_path} deleted successfully.")
            else:
                logger.error(f"File {file_path} does not exist.")
        except PermissionError:
            logger.error(f"Permission denied, unable to delete file {file_path}.")
        except Exception as e:
            logger.error(f"An error occurred while trying to delete file '{file_path}': {e}")
