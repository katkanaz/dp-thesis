package api

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

func NewRouter() *chi.Mux {
	r := chi.NewRouter()

	fileServer := http.FileServer(http.Dir("./data/img"))
	r.Handle("/img/*", http.StripPrefix("/img/", fileServer))
	r.Get("/sugars", getSugars)
	// r.Get("/sugars/{abrev}", getResultsSpecificSugar) // TODO: still needed?

	// r.Get("/results", getResults)

	return r
}




// nginx
// -> / -> html.index js
// -> /api -> redirect to backend and remove /api
