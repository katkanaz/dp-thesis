from abc import ABC, abstractmethod
from pathlib import Path
import os
from typing import Set, Tuple
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

    def get_pq_result(self, config: Config) -> None:
        """
        Retrieve PatternQuery results archive locally via symbolic link.

        :param config: Config object
        """
        pass

    def create_sym_links(self):
        # TODO: add docs
        pass

    def download_structures(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve mmCIF structure files locally via symbolic links.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        pass

    def download_validation_files(self, config: Config, pdb_ids: Set[str], dest_path: Path) -> None:
        """
        Retrieve XML validation files locally via symbolic links.

        :param config: Config object
        :param pdb_ids: IDs of structures to use for creating the file list 
        :param dest_path: Download destination directory
        """
        pass


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
        self.download_from_mirror("validation-files", dest_path, file_list_path)
