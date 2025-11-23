package main

import (
	"dp-be/api"
	"net/http"
)


func main() {
	r := api.NewRouter()

	http.ListenAndServe(":8081", r)
}
