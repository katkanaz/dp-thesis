export type ResidueId = {
	label_asym_id: string,
	struct_oper_id: string,
	label_seq_id: number,
}

export type Motif = {
	surrounding: string,
	sugar: string,
	original_structure: string,
	residue_ids: ResidueId[],
	score: number,
	residue_types:string[],
	transformation: number[],

} 

export type ComputedStructure = { 
	pdb_id: string,
	afdb_id: string,
	title: string,
	organism: string[],
	plddt: number,
	af_version: string,
	af_revision: number,
	motifs: Motif[],
};


export const getResults = async (): Promise<ComputedStructure[]> => {
    const res = await fetch("/api/results");
    if (!res.ok) throw new Error("Failed to fetch results");
    const data: ComputedStructure[] = await res.json();
    return data;
};

export const getCompStruct = async (afid: string): Promise<ComputedStructure> => {
    const res = await fetch(`/api/results/${afid}`);
    if (!res.ok) throw new Error("Failed to fetch the computed structure");
    const data: ComputedStructure = await res.json();
    return data;
};
