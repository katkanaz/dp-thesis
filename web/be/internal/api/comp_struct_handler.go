package api

import (
	"dp-be/internal/functools"
	"dp-be/internal/set"
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"time"
)

type OptionItem struct {
	Id int `json:"id"`
	Value string `json:"value"`
}

type PlddtRange struct {
	Min float32 `json:"min"`
	Max float32 `json:"max"`
}

type FilterOptions struct {
	Sugars []OptionItem `json:"sugars"`
	PlddtRange PlddtRange `json:"plddt_range"`
	Organisms []OptionItem `json:"organisms"`
	PdbStructures []OptionItem `json:"pdb_structures"`
}

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


func getDateTime(dir_path string, file_sufix string) (string, string) {
	file, err := getNewest(dir_path, file_sufix)
	if err != nil {
		panic (err)
	}

	fileName := filepath.Base(file)
	datetimePart := strings.TrimSuffix(fileName, file_sufix)
	layout := "2006-01-02T15-04-05"

	t, err := time.Parse(layout, datetimePart)
	if err != nil {
		panic(err)
	}

	dateOnly := t.Format("2006-01-02")
	timeOnly := t.Format("15-04-05")
	return dateOnly, timeOnly
}


func getLastModifiedDate(w http.ResponseWriter, r *http.Request) {
	dateOnly, _ := getDateTime("data/workflow_runs/", "_merged.json")
	lastUpdated := LastUpdated{
		Date: dateOnly,
	}

	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(lastUpdated); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}


func ExtractOptions() error {
	dateOnly, timeOnly := getDateTime("data/workflow_runs/", "_merged.json")
	data := getComputedStructures()

	plddtRange := PlddtRange{
		Min: float32(math.Inf(+1)),
		Max: float32(math.Inf(-1)),
	}
	sugarSet := set.NewSet[string]()
	organismSet := set.NewSet[string]() 
	pdbStructSet := set.NewSet[string]()

	for _, structure := range data {
		for _, organism := range structure.Organism {
			organismSet.Add(organism)
		}
		if structure.Plddt < plddtRange.Min {
			plddtRange.Min = structure.Plddt
		}
		if structure.Plddt > plddtRange.Max {
			plddtRange.Max = structure.Plddt
		}
		for _, motif := range structure.Motifs {
			sugarSet.Add(motif.Sugar)
			pdbStructSet.Add(motif.OriginalStructure)
		}
	}

	o := FilterOptions{
		PlddtRange: plddtRange,
		Sugars: functools.Map(sugarSet.ToList(), func(e string, i int) OptionItem {return OptionItem{Id: i, Value: e}}),
		Organisms: functools.Map(organismSet.ToList(), func(e string, i int) OptionItem {return OptionItem{Id: i, Value: e}}),
		PdbStructures: functools.Map(pdbStructSet.ToList(), func(e string, i int) OptionItem {return OptionItem{Id: i, Value: e}}),
	}

	options, err := json.MarshalIndent(o, "", "  ")
	if err != nil {
		return err
	}

	filename := fmt.Sprintf("data/workflow_runs/%sT%s_options.json", dateOnly, timeOnly)

	return os.WriteFile(filename, options, 0644)
}


func getComputedStructures() []ComputedStructure {
	var computedStructures []ComputedStructure
	file, err := getNewest("data/workflow_runs/", "_merged.json")
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


func getFilterOptions(w http.ResponseWriter, r *http.Request) {
	var filterOptions FilterOptions
	file, err := getNewest("data/workflow_runs/", "_options.json")
	if err != nil {
		panic (err)
	}
	opts, err := os.Open(file)
	if err != nil {
		panic(err)
	}
	defer opts.Close()

	if err := json.NewDecoder(opts).Decode(&filterOptions); err != nil {
		panic(err)
	}

	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(filterOptions); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
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

func getStats(w http.ResponseWriter, r *http.Request) {}
