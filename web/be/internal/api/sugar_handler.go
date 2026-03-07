package api

import (
	"encoding/json"
	"net/http"
	"os"
)


type Sugar struct {
	Name string `json:"name"`
	Abrev string `json:"abrev"`
	Img string `json:"img"`
}

func GetSugarInfo() []Sugar {
	var sugarAbrevs []string
	processedFile, err := os.Open("data/processed_sugars.json")
	if err != nil {
		panic(err)
	}
	defer processedFile.Close()

	if err := json.NewDecoder(processedFile).Decode(&sugarAbrevs); err != nil {
		panic(err)
	}

	var sugars []Sugar
	sugarFile, err := os.Open("data/sugars.json")
	if err != nil {
		panic(err)
	}
	defer sugarFile.Close()

	if err := json.NewDecoder(sugarFile).Decode(&sugars); err != nil {
		panic(err)
	}

	filterMap := make(map[string]bool)
	for _, abrev := range sugarAbrevs {
		filterMap[abrev] = true
	}

	var filtered []Sugar
	for _, sugar := range sugars {
		if filterMap[sugar.Abrev] {
			filtered = append(filtered, sugar)
		}
	}

	return filtered

}

func getSugars(w http.ResponseWriter, r *http.Request) {
	sugars := GetSugarInfo()
	
	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(sugars); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
