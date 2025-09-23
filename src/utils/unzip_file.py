from pathlib import Path
import shutil
from zipfile import ZipFile


def unzip_all(src_path: Path, dest_path: Path) -> None:
    """
    Extract a zip archive into <dest_path>

    :param src_path: Path to the .zip file
    :param dest_path: Directory to extract the zip archive into
    """

    with ZipFile(src_path, "r") as zip_ref:
        zip_ref.extractall(dest_path)


def unzip_single_file(src_path: Path, dest_path: Path, file_to_extract: str) -> Path:
    """
    Extract a single file from a zip archive into <dest_path>, no folder structure is preserved.

    :param src_path: Path to the .zip file
    :param dest_path: Directory to save the extracted file
    :param file_to_extract: Path to the file inside the zip, relative to the zip root
    :return: Path to the extracted file
    :raises FileNotFoundError: If <file_to_extract> is not found inside the zip archive
    """

    output_path = dest_path / Path(file_to_extract).name

    with ZipFile(src_path, "r") as zip_ref:
        if file_to_extract not in zip_ref.namelist():
            raise FileNotFoundError(f"{file_to_extract} not found in the archive")

        with zip_ref.open(file_to_extract) as zf, open(output_path, "wb") as f:
            shutil.copyfileobj(zf, f)


    return output_path
    
