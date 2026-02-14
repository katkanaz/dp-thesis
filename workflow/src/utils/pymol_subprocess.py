from pathlib import Path
from logger import logger
from subprocess import Popen, PIPE

def run_pymol_subprocess(file_to_run: str, argument_list: list[str]):
    cmd = [
        "../pymol-venv/bin/python",
        "-m",
        file_to_run]

    cmd.extend(argument_list)

    cmd = " ".join(cmd)

    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True) as proc:
        assert proc.stdout is not None, "stdout is set to PIPE in Popen"
        for line in proc.stdout:
            logger.info(f"STDOUT: {line.strip()}")
        assert proc.stderr is not None, "stderr is set to PIPE in Popen"
        for line in proc.stderr:
            logger.error(f"STDERR: {line.strip()}")

    if proc.returncode != 0:
        logger.error(f"PyMOL subprocess exited with code {proc.returncode}")
        raise Exception("PyMOL subprocess exited abnormally")
    else:
        logger.info("PyMOL subprocess completed successfully")
