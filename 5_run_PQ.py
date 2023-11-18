import json
import os
import shutil
import subprocess
import zipfile

from tempfile import TemporaryDirectory
from pathlib import Path


PQ_WORKING_PATH = Path(__file__).parent.parent / "PatternQuery_1.1.21.12.14a"
RESULTS_FOLDER = Path(__file__).parent.parent / "results"
DATA_FOLDER = Path(__file__).parent.parent / "data"


more_than_one_pattern = []			# just to check no more than one pattern for specific ResidueID was found
PQ_couldnt_find_pattern = []		# some ResidueID couldn"t be found by PQ because they have different ResidueID somehow 
result_folder_not_created = []		# just in case something else goes wrong


def create_config(structure, residues, sugar):
	"""
	Creates config file for the given structure.
	Every stucture can contain 0 - n residues of interest specified by <sugar>.
	If the current structure does not contain any rezidue of sugar of interest, empty list is returned - so the program can jump to the next structure.
	If at least one residue of interest is present:
	For every residue a separate query is needed. Therefore one config file with 1-n queries is created per structure.
	Then it is saved and a list of all query names is returnd.
	Name is in a form <pdb>_<name>_<num>_<chain>_*<key_sensitive_tag>*.pdb
	"""
	config = {
		"InputFolders": [
			str(PQ_WORKING_PATH / "structures"),
		],
		"Queries": [],
		"StatisticsOnly": False,
		"MaxParallelism": 2
	}
	query_names = []
	# PQ queries are not key sensitive but there are structures which contain
	# two chains with the same letter but one upper and the other lower.
	# In that case eg. residues "GLC 1 M" and "GLC 1 m" would have the same
	# query in PQ sense. Therefore, "_2" is added to such queries.
	key_sensitive_check = []
	for residue in residues:
		if residue["name"] == sugar:
			key = f"{residue['num']}_{residue['chain']}"
			if key.upper() in key_sensitive_check or key.lower() in key_sensitive_check:
				query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}_2"
			else:
				key_sensitive_check.append(key)
				query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}"
			query_names.append(query_id)
			query_str = f"ResidueIds('{residue['num']} {residue['chain']}').AmbientResidues(5)"
			config["Queries"].append({"Id": query_id, "QueryString": query_str})

	if query_names:
		# create respective config file for current structure, with queries for every ligand of sugar of interest in that structure
		with open(PQ_WORKING_PATH / "configuration.json", "w") as f:
			json.dump(config, f, indent=4)

	return query_names


def extract_results(target, zip_result_folder, query_names):
	"""
	Results are present in the zip folder, where every query has its own subfolder
	with the name same as was its query name: <pdb>_<name>_<num>_<chain>_*<key_sensitive_tag>*.pdb
	Each query is expected to have only one pattern found.
	So the results are unzipped and the each pattern pdb (surrounding of one sugar)
	is renamed and moved to one common folder.
	"""
	with TemporaryDirectory() as temp_dir:
		with zipfile.ZipFile(zip_result_folder, "r") as zip_ref:
			zip_ref.extractall(temp_dir)
			for dir in query_names:
				results_path = Path(temp_dir) / dir / "patterns"
				if not results_path.exists():
					PQ_couldnt_find_pattern.append(dir)
					continue
				# It is expected to have only one pattern found for one query, but checking just in case
				if len(os.listdir(results_path)) > 1:
					more_than_one_pattern.append(dir) 
				for file in results_path.iterdir():
					Path(file).rename(results_path / f"{dir}.pdb")  # rename the pattern so it is distinguishable
				src = results_path / f"{dir}.pdb"
				shutil.move(src, target)


def main(sugar):
	with open(RESULTS_FOLDER / "categorization" / "flitered_ligands.json", "r") as f:
		ligands = json.load(f)
	
	target_dir = RESULTS_FOLDER / "binding_sites" / sugar
	target_dir.mkdir(exist_ok=True, parents=True)

	for structure, residues in ligands.items():
		structure = structure.lower()
		query_names = create_config(structure, residues, sugar)
		if not query_names:
			continue
		# copy current structure to ./structures dir which is used as source by PQ.
		src = DATA_FOLDER / "mmCIF_files" / f"{structure}.cif"
		dst = PQ_WORKING_PATH / f"structures\\{structure}.cif"
		shutil.copyfile(src, dst)

		# run PQ
		cmd = [
			f"{PQ_WORKING_PATH}\\WebChemistry.Queries.Service.exe",
			PQ_WORKING_PATH ,
			f"{PQ_WORKING_PATH}\\configuration.json"
		]
		subprocess.run(cmd, shell=True)

		zip_result_folder = PQ_WORKING_PATH / "result\\result.zip"
		if not zip_result_folder.exists():
			result_folder_not_created.append(structure)
			# delete the current structure from ./structures directory and continue to the next structure
			Path(PQ_WORKING_PATH / f"structures\\{structure}.cif").unlink()
			continue
		
		extract_results(target_dir, zip_result_folder, query_names)

		# delete the result folder and also the current structure from ./structures so the new one can be copied there
		(PQ_WORKING_PATH / f"structures\\{structure}.cif").unlink()
		shutil.rmtree(PQ_WORKING_PATH / "result")

	print("more patterns for one id:", more_than_one_pattern)
	print()
	print("PQ could not find these patterns:", PQ_couldnt_find_pattern)
	print()
	print("result folder not created:", result_folder_not_created)




if __name__ == "__main__":
    main("FUC")
