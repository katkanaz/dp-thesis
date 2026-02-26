package api

type Motif struct {}

type ComputedStructure struct {
	Pdbid string `json:"pdb_id"`
	Afdbid string `json:"afdb_id"`
	Title string `json:"title"`
	Organism []string `json:"organism"`
	Plddt float32
	Afversion string
	Afrevision int
	Motifs []Motif
}
