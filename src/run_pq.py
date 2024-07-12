from argparse import ArgumentParser
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import zipfile

from config import Config


more_than_one_pattern = []			# just to check no more than one pattern for specific ResidueID was found
pq_couldnt_find_pattern = []		# some ResidueID couldn't be found by PQ because they have different ResidueID somehow 
result_folder_not_created = []		# just in case something else goes wrong

def create_config(structure: str, residues, sugar: str) -> list:
	#FIXME: Reword docstring, residues type and description
	"""
	Create config file for the given structure

	Every stucture can contain 0 - n residues of interest specified by <sugar>.
	If the current structure does not contain any rezidue of sugar of interest, empty list is returned - so the program can jump to the next structure.
	If at least one residue of interest is present:
	For every residue a separate query is needed. Therefore one config file with 1-n queries is created per structure.
	Then it is saved and a list of all query names is returnd.
	Name is in a form <pdb>_<name>_<num>_<chain>_*<case_sensitive_tag>*.pdb

	:param structure: PDB ID of structure
	:param residues [TODO:type]: [TODO:description]
	:param sugar: The sugar for which the representative binding site is being defined
	:return: List of query IDs
	"""

	pq_config = {
		"InputFolders": [
			str(config.pq_structures),
		],
		"Queries": [],
		"StatisticsOnly": False,
		"MaxParallelism": 2
	}
	query_names = []

	#TODO: reword
	# PQ queries are not case sensitive but there are structures which contain
	# two chains with the same letter but one upper and the other lower.
	# In that case eg. residues "GLC 1 M" and "GLC 1 m" would have the same
	# query in PQ sense. Therefore, tag "_2" is added to such queries.
	case_sensitive_check = []
	for residue in residues:
		if residue["name"] == sugar:
			case = f"{residue['num']}_{residue['chain']}"
			if case.upper() in case_sensitive_check or case.lower() in case_sensitive_check:
				query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}_2"
			else:
				case_sensitive_check.append(case)
				query_id = f"{structure}_{residue['name']}_{residue['num']}_{residue['chain']}"
			query_names.append(query_id)
			query_str = f"ResidueIds('{residue['num']} {residue['chain']}').AmbientResidues(5)"
			pq_config["Queries"].append({"Id": query_id, "QueryString": query_str})

	if query_names:
		# create respective config file for current structure, with queries for every ligand of sugar of interest in that structure
		with open(config.pq_working_path / "configuration.json", "w") as f:
			json.dump(pq_config, f, indent=4)

	return query_names


def extract_results(target: Path, zip_result_folder: Path, query_names: list) -> None:
	#FIXME: Reword the docstring
	"""
	Unzip the results and rename and move each sugar surrounding (pattern) to one common folder

	Results are present in the zip folder, where every query has its own subfolder
	with the name same as was its query name: <pdb>_<name>_<num>_<chain>_*<key_sensitive_tag>*.pdb
	Each query is expected to have only one pattern found

	:param target: Common folder to move resulting binding sites to
	:param zip_result_folder: Path to zip folder containing PQ results
	:param query_names: List of query IDs
	"""

	with TemporaryDirectory() as temp_dir:
		with zipfile.ZipFile(zip_result_folder, "r") as zip_ref:
			zip_ref.extractall(temp_dir)
			for query_name in query_names: 
				results_path = Path(temp_dir) / query_name / "patterns"
				if not results_path.exists():
					pq_couldnt_find_pattern.append(query_name)
					continue
				# It is expected to have only one pattern found for one query, but checking just in case
				if len(os.listdir(results_path)) > 1:
					#global END_FLAG
					#END_FLAG = True
					#return
					more_than_one_pattern.append(query_name)
					continue
				for file in results_path.iterdir():
					Path(file).rename(results_path / f"{query_name}.pdb")  # rename the pattern so it is distinguishable
				src = results_path / f"{query_name}.pdb"
				shutil.move(str(src), str(target))


def main(sugar: str, config: Config) -> None:
	with open(config.categorization_results / "filtered_ligands.json", "r") as f:
		ligands = json.load(f)
	
	target_dir = config.binding_sites / sugar
	target_dir.mkdir(exist_ok=True, parents=True)

	for structure, residues in ligands.items():
		structure = structure.lower()
		query_names = create_config(structure, residues, sugar)
		if not query_names:
			continue
		# Copy current structure to ./structures dir which is used as source by PQ.
		src = config.mmcif_files / f"{structure}.cif"
		dst = config.pq_structures / f"{structure}.cif"
		shutil.copyfile(src, dst)

		#TODO: extract to function
		# Run PQ
		cmd = [
			f"mono {config.pq_working_path}/WebChemistry.Queries.Service.exe {config.pq_results} {config.pq_working_path}/configuration.json"
		]
		subprocess.run(cmd, shell=True)

		zip_result_folder = config.pq_results / "result/result.zip"
		if not zip_result_folder.exists():
			result_folder_not_created.append(structure)
			# delete the current structure from ./structures directory and continue to the next structure
			Path(config.pq_structures / f"{structure}.cif").unlink()
			continue
		
		extract_results(target_dir, zip_result_folder, query_names)

		#if END_FLAG:
			#break

		# Delete the result folder and also the current structure from ./structures so the new one can be copied there
		(config.pq_structures / f"{structure}.cif").unlink()
		shutil.rmtree(config.pq_results / "result")

	print("more patterns for one id:", more_than_one_pattern, end="\n\n")
	print("PQ could not find these patterns:", pq_couldnt_find_pattern, end="\n\n")
	print("result folder not created:", result_folder_not_created)


if __name__ == "__main__":
	parser = ArgumentParser()
	
	parser.add_argument("-s", "--sugar", help="Three letter code of sugar", type=str, required=True)
	
	args = parser.parse_args()

	config = Config.load("config.json")

	config.pq_structures.mkdir(exist_ok=True, parents=True)
	config.pq_results.mkdir(exist_ok=True, parents=True)
	
	main(args.sugar, config)
