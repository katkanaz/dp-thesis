from abc import ABC, abstractmethod
from pathlib import Path
import os
from typing import Set, Tuple, List
import subprocess

from logger import logger
from configuration import Config

class DataSourceHandler(ABC):
    """
    Abstract base class for handeling the data source. This class should not be instantiated direclty.
    Instead, use `DataSourceHandler.create()` to obtain an instance of a concrete subclass.
    """

    @abstractmethod
    def get_pq_result(self, config: Config) -> None:
        """
        Retrieve PatternQuery results archive from the data source.

        :param config: Config object
        """
        ...

    @abstractmethod
    def download_structures(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve mmCIF structure files from the data source.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        ...

    @abstractmethod
    def download_validation_files(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve XML validation files from the data source.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        ...

    @classmethod
    def create(cls):
        """
        Create a DataSourceHandler instance based on the DATA_SOURCE environment variable.

        :returns DataSourceHandler: An instance of LocalDataHandler or RemoteDataHandler.
        :raises ValueError: If DATA_SOURCE is unrecognized.
        """
        source = os.getenv("DATA_SOURCE")

        logger.info(f"Creating data source of type {source}")

        if source == "local" or not source:
            return LocalDataHandler()
        elif source == "remote":
            return RemoteDataHandler()
        else:
            raise ValueError(f"Unknown data source: '{source}'")


class LocalDataHandler(DataSourceHandler):
    """
    Concrete DataSourceHandler subclass that represents the data source being local.
    """

    def create_sym_links(self, file_list: List[str], src_dir: Path, dest_dir: Path) -> None:
        """
        Create symbolic links in <dest_dir> for each file in file_list, pointing to the files in <src_dir>.

        :param file_list: List of files to link
        :param src_dir: Source directory of files to link
        :param dest_dir: Destination directory where to link the files
        """

        dest_dir.mkdir(parents=True, exist_ok=True)

        for file_name in file_list:
            src_file = src_dir / file_name
            dest_link = dest_dir / file_name

            if not src_file.exists():
                logger.warning(f"Source file does not exist: {src_file}")
                continue

            if dest_link.exists() or dest_link.is_symlink():
                dest_link.unlink()

            dest_link.symlink_to(src_file)

    def get_pq_result(self, config: Config) -> None:
        """
        Retrieve PatternQuery results archive locally via symbolic link.

        :param config: Config object
        """

        logger.info("Downloading PQ results")
        self.create_sym_links(["result.zip"], config.init_pq_dir, config.sugar_binding_patterns_dir) # TODO: Double check folder logic when creating script for init pq

    def build_filenames_list(self, pdb_ids: Set[str], extension: str, name_sufix: str = "") -> List[str]:
        """
        Return list of full filenames given a set of PDB IDs, an extentio and an optional sufix.

        :param pdb_ids: PDB IDs of to build the file names (structures to work with)
        :param extension: File extenstion of the specific file
        :param name_sufix: Optional name sufix (mostly for validation files, to follow RCSB naming convention)
        :return: List of complete file names
        """

        return [f"{pdb_id}{name_sufix}{extension}" for pdb_id in pdb_ids]


    def download_structures(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve mmCIF structure files locally via symbolic links.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        
        logger.info("Downloading structures files")
        self.create_sym_links(self.build_filenames_list(pdb_ids, ".cif.gz"), config.pdb_mirror_structures, dest_path)


    def download_validation_files(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve XML validation files locally via symbolic links.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        
        logger.info("Downloading validation files")
        self.create_sym_links(self.build_filenames_list(pdb_ids, ".xml.gz", "_validation"), config.pdb_mirror_validation_files, dest_path)


class RemoteDataHandler(DataSourceHandler):
    """
    Concrete DataSourceHandler subclass that represents the data source being remote.
    """

    def get_rsync_info(self) -> Tuple[str, str, str]:
        # TODO: add docs
        user = os.getenv("RSYNC_USER")
        assert user is not None, "RSYNC_USER is missing from environment"
        password = os.getenv("RSYNC_PASSWORD")
        assert password is not None, "RSYNC_USER is missing from environment"
        host = os.getenv("RSYNC_HOST")
        assert host is not None, "RSYNC_USER is missing from environment"

        return user, password, host


    def get_pq_result(self, config: Config) -> None:
        """
        Retrieve PatternQuery results archive from the remote host via rsync.

        :param config: Config object
        """

        user, password, host = self.get_rsync_info() 

        src_path = f"{user}@{host}:/storage/brno2/home/{user}/pq-runs/2025-07-19T17-44-results/result/result.zip" # FIXME: Not abstract enough 
        dest_path = Path(config.sugar_binding_patterns_dir)

        logger.info("Downloading PQ results")

        cmd = [
            "/usr/bin/rsync",
            "-ratlz",
            f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
            src_path,
            dest_path
        ]

        subprocess.run(cmd, check=True) # TODO: add runtimeerror


    def create_file_list(self, config: Config, pdb_ids: Set[str], file_name: str, extension: str, name_sufix = "") -> Path:
        """
        Create a text file containing file names based on <pdb_ids> to download for rsync.

        :param config: Config object
        :param pdb_ids: IDs of structures to create the file contents
        :param file_name: Name of the file to save the file list into
        :param extension: File extension of the files to download
        :return: Path to file list
        """

        logger.info("Creating file list for rsync")

        with open(config.run_data_dir / file_name, "w", encoding="utf8") as f:
            for pdb_id in pdb_ids:
                f.write(f"{pdb_id}{name_sufix}{extension}\n")

        return config.run_data_dir / file_name 


    def download_from_mirror(self, src_dir: str, dest_path: Path, file_list_path: Path) -> None:
        # TODO: add docs
        user, password, host = self.get_rsync_info() 

        src_path = f"{user}@{host}:/storage/brno2/home/{user}/pdb-mirror/{src_dir}"

        cmd = [
            "/usr/bin/rsync",
            "-ratL",
            f"--rsh=/usr/bin/sshpass -p {password} ssh -o StrictHostKeyChecking=no",
            f"--files-from={file_list_path}",
            src_path,
            dest_path
        ]

        subprocess.run(cmd, check=True) # TODO: add runtimeerror
         # FIXME: catch if rsync skips missing files


    def download_structures(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve mmCIF structure files from the remote host via rsync.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """

        file_list_path = self.create_file_list(config, pdb_ids, "structures_file_list.txt", ".cif.gz")
        logger.info("Downloading structures files")
        self.download_from_mirror("structures", dest_path, file_list_path)


    def download_validation_files(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve XML validation files from the remote host via rsync.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """

        file_list_path = self.create_file_list(config, pdb_ids, "validation_file_list.txt", ".xml.gz", "_validation")
        logger.info("Downloading validation files")
        self.download_from_mirror("validation-files", dest_path, file_list_path) # TODO: extract mirror struct definition to config
