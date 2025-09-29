import argparse
import json
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
import os

from logger import logger


class UserConfig(BaseModel):
    data_dir: Path
    results_dir: Path
    images_dir: Path
    mv_dir: Path
    pq_dir: Path

    pdb_ids_list: Optional[List[str]] = None
    skip_ids: Optional[List[str]] = None
    data_run: Optional[str] = None


    @classmethod
    def load_json(cls, file_path: Union[Path, str]) -> "UserConfig":
        with open(file_path, "r") as f:
            data = json.load(f)
        user_config = cls(**data)

        return user_config


class Config():
    user_cfg: UserConfig

    run_data_dir: Path

    log_path: Path
    sugar_binding_patterns_dir: Path
    init_pq_dir: Path
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
    raw_surroundings_dir: Path
    filtered_surroundings_dir: Path
    clusters_dir: Path
    structure_motif_search_dir: Path
    dendrograms_dir: Path
    tanglegrams_dir: Path


    @classmethod
    def load(cls, file_path: Union[Path, str], sugar: Union[str, None], need_data_run: bool, args: Union[argparse.Namespace, None], force_new: bool = False) -> "Config":
        config = cls()
        config.user_cfg = UserConfig.load_json(file_path)
        if args is not None and args.test_mode:
            assert config.user_cfg.pdb_ids_list is not None, "If run in test mode 'pdb_ids_list' config value cannot be None"
        current_run = config.get_current_run(force_new)
        data_run = config.get_data_run(config.user_cfg.data_dir, config.user_cfg.data_run) if need_data_run else None
        config._update_relative_paths(sugar, current_run, data_run)

        return config


    def _update_relative_paths(self, sugar: Union[str, None], current_run: str, data_run: Union[str, None]) -> None:
        if data_run is None:
            data_run = current_run

        self.run_data_dir = self.user_cfg.data_dir / data_run

        path_to_logfile = f"ligand_sort/{data_run}/{data_run}.log"

        self.sugar_binding_patterns_dir = self.user_cfg.data_dir / f"{data_run}/sugar_binding_patterns"
        self.components_dir = self.user_cfg.data_dir / f"{data_run}/components"
        self.mmcif_files_dir = self.user_cfg.data_dir / f"{data_run}/mmcif_files"
        self.modified_mmcif_files_dir = self.user_cfg.data_dir / f"{data_run}/modified_mmcif_files"
        self.no_o6_mmcif_dir = self.user_cfg.data_dir / f"{data_run}/no_o6_mmcif"
        self.validation_files_dir = self.user_cfg.data_dir / f"{data_run}/validation_files"

        self.categorization_dir = self.user_cfg.results_dir / f"ligand_sort/{data_run}/categorization"
        self.validation_dir = self.user_cfg.results_dir / f"ligand_sort/{data_run}/validation"
        self.mv_run_dir = self.user_cfg.results_dir / f"ligand_sort/{data_run}/mv_run"
        self.graph_analysis_dir = self.user_cfg.results_dir / f"ligand_sort/{data_run}/graph_analysis"
        self.residue_graphs_dir = self.user_cfg.images_dir / f"ligands/{data_run}/residue_graphs"

        # Sugars are always newer than the data run, since they are downloaded by the second part of the process
        self.sugars_dir = self.user_cfg.data_dir / f"{data_run}/sugars"

        if sugar is not None:
            path_to_logfile = f"motif_based_search/{sugar}/{current_run}/{current_run}.log"
            self.pq_run_dir = self.user_cfg.results_dir / f"motif_based_search/{sugar}/{current_run}/pq_run"
            self.raw_surroundings_dir = self.user_cfg.results_dir / f"motif_based_search/{sugar}/{current_run}/raw_surroundings"
            self.filtered_surroundings_dir = self.user_cfg.results_dir / f"motif_based_search/{sugar}/{current_run}/filtered_surroundings"
            self.clusters_dir = self.user_cfg.results_dir / f"motif_based_search/{sugar}/{current_run}/clusters"
            self.structure_motif_search_dir = self.user_cfg.results_dir / f"motif_based_search/{sugar}/{current_run}/structure_motif_search"
            self.dendrograms_dir = self.user_cfg.images_dir / f"surroundings/{sugar}/{current_run}/dendrograms"
            self.tanglegrams_dir = self.user_cfg.images_dir / f"surroundings/{sugar}/{current_run}/tanglegrams"


        self.log_path = self.user_cfg.results_dir / path_to_logfile

    
    @classmethod
    def get_data_run(cls, data_dir: Path, data_run: Union[str, None]) -> str: # TODO: add types
        if data_run is not None:
            assert data_run != "", "User defined 'data_run' cannot be empty string"
            return data_run

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
                current_datetime = f.read().strip()

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
