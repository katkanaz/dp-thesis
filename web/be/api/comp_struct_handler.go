package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"time"
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
	ResidueIds []ResidueId `json:"residue_ids"`
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

type LastUpdated struct {
	Date string `json:"date"`
}


func getNewest(dir string, sufix string) (string, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return "", err
	}

	var newestTime time.Time
	var newestFile string
	layout := "2006-01-02T15-04-05"

	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		name := entry.Name()

		if !strings.HasSuffix(name, sufix) {
			continue
		}

		datetimePart := strings.TrimSuffix(name, sufix)

		t, err := time.Parse(layout, datetimePart)
		if err != nil {
			continue
		}

		if t.After(newestTime) {
			newestTime = t
			newestFile = filepath.Join(dir, name)
		}
	}

	if newestFile == "" {
		return "", fmt.Errorf("No matching files found")
	}

	return newestFile, nil
}


func getLastModifiedDate(w http.ResponseWriter, r *http.Request) {
	file, err := getNewest("data/merged/", "_merged.json")
	if err != nil {
		panic (err)
	}

	fileName := filepath.Base(file)
	datetimePart := strings.TrimSuffix(fileName, "_merged.json")
	layout := "2006-01-02T15-04-05"

	t, err := time.Parse(layout, datetimePart)
	if err != nil {
		panic(err)
	}

	dateOnly := t.Format("2006-01-02")
	lastUpdated := LastUpdated{
		Date: dateOnly,
	}

	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(lastUpdated); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
}


func getComputedStructures() []ComputedStructure {
	var computedStructures []ComputedStructure
	file, err := getNewest("data/merged/", "_merged.json")
	if err != nil {
		panic (err)
	}
	merged, err := os.Open(file)
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

func getStats(w http.ResponseWriter, r *http.Request) {

}
