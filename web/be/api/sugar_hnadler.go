package api

import (
	"encoding/json"
	"net/http"
)

func getSugars(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Sugar abrevs"))
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode() // NOTE: does it write status ok?
}


func getResultsSpecificSugar(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Results for given sugar"))

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode() // NOTE: does it write status ok?
}
