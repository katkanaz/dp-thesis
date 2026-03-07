package main

import (
	"dp-be/internal/api"
	"net/http"
)


func main() {
	api.ExtractOptions()
	r := api.NewRouter()

	http.ListenAndServe(":8081", r)
}
