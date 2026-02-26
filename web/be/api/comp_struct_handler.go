package api

import (
	"encoding/json"
	"net/http"
	"os"
	"slices"
)

type ResidueId struct {
	LabelAsymId string `json:"label_asym_id"`
	StructOperId string `json:"struct_oper_id"`
	LabelSeqId int `json:"label_seq_id"`
}

type Motif struct {
	Surrounding string `json:"surrounding"`
	Sugar string `json:"sugar"`
	OriginalStructure string `json:"original_struct"`
	Residueids []ResidueId `json:"residue_ids"`
	Score float32 `json:"score"`
	ResidueTypes []string `json:"residue_types"`
	Transformation []float32 `json:"transformation"`
}

type ComputedStructure struct {
	PdbId string `json:"pdb_id"`
	AfdbId string `json:"afdb_id"`
	Title string `json:"title"`
	Organism []string `json:"organism"`
	Plddt float32 `json:"plddt"`
	AfVersion string `json:"af_version"`
	AfRevision int `json:"af_revision"`
	Motifs []Motif `json:"motifs"`
}


func getComputedStructures() []ComputedStructure {
	var computedStructures []ComputedStructure
	merged, err := os.Open("data/merged.json")
	if err != nil {
		panic(err)
	}
	defer merged.Close()

	if err := json.NewDecoder(merged).Decode(&computedStructures); err != nil {
		panic(err)
	}

	return computedStructures
}


func getAllResults(w http.ResponseWriter, r *http.Request) {
	results := getComputedStructures()
	
	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(results); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}


func getCompStructDetail(w http.ResponseWriter, r *http.Request) {
	afid := r.PathValue("afid")
	results := getComputedStructures()
	index := slices.IndexFunc(results, func(c ComputedStructure) bool {
		return c.AfdbId == afid
	})
	if index == -1 {
		http.Error(w, "Invalid AlphaFold ID", http.StatusBadRequest)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(results[index]); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
