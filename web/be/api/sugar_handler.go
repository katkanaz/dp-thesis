package api

import (
	"dp-be/data"
	"encoding/json"
	"net/http"
)

func getSugars(w http.ResponseWriter, r *http.Request) {
	sugars := data.GetSugarInfo()
	
	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(sugars); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}


// func getResultsSpecificSugar(w http.ResponseWriter, r *http.Request) {
// 	w.Write([]byte("Results for given sugar"))
//
// 	w.Header().Set("Content-Type", "application/json")
// 	w.WriteHeader(http.StatusOK)
// 	json.NewEncoder(w).Encode() // NOTE: does it write status ok?
// }
