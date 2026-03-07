import { MultiSelectOption } from "../components/MultiSelect";

export type ResidueId = {
	label_asym_id: string,
	struct_oper_id: string,
	label_seq_id: number,
}

export type Motif = {
	surrounding: string,
	sugar: string,
	original_struct: string,
	residue_ids: ResidueId[],
	score: number,
	residue_types: string[],
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

export type LastUpdated = {
	date: string,
}

export type MotifResidueInfo = {
    type: string,
    label_seq: number,
    label_asym: string,
}

export type PlddtRange = {
    min: number,
    max: number,
}

export type FilterOptions = {
    sugars: MultiSelectOption[],
    plddt_range: PlddtRange,
    organisms: MultiSelectOption[],
    pdb_structures: MultiSelectOption[],
}

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

export const getLastModified = async (): Promise<LastUpdated> => {
    const res = await fetch(`/api/last-modified`);
    if (!res.ok) throw new Error("Failed to fetch last modified date");
    const data: LastUpdated = await res.json();
    return data;
}

export const mergeRisudeInfo = (residue_types: string[], residue_ids: ResidueId[]): MotifResidueInfo[] => {
    const res: MotifResidueInfo[] = [];
    for (let i = 0; i < residue_ids.length; i++) {
        res.push({
            type: residue_types[i],
            label_seq: residue_ids[i].label_seq_id,
            label_asym: residue_ids[i].label_asym_id,
        });
    }
    return res;
}

export const getFilterOptions = async (): Promise<FilterOptions> => {
    const res = await fetch(`/api/filter-options`);
    if (!res.ok) throw new Error("Failed to fetch filter options");
    const data: FilterOptions = await res.json();
    return data;
}
