package set

type Set[T comparable] map[T]struct{}

func NewSet[T comparable]() Set[T] {
	return make(Set[T])
}

func (s Set[T]) Add(e T) Set[T] {
	s[e] = struct{}{}
	return s
}

func (s Set[T]) Remove(e T) Set[T] {
	delete(s, e)
	return s
}

func (s Set[T]) Has(e T) bool {
	_, ok := s[e]
	return ok
}

func From[T comparable] (elms ...T) Set[T] {
	s := make(Set[T], len(elms))
	for _, e := range elms {
		s.Add(e)
	}
	return s
}

func (s Set[T]) ToList() []T {
	l := make([]T, 0, len(s))
	for e := range s {
		l = append(l, e)
	}
	return l
}
