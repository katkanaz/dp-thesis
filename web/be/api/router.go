package api

import (
	"github.com/go-chi/chi/v5"
)

func NewRouter() *chi.Mux {
	r := chi.NewRouter()

	r.Get("/sugars", getSugars)
	r.Get("/sugars/{abrev}", getResultsSpecificSugar)

	return r
}
