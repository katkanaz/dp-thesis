package functools

func Map[T any, R any](items []T, fn func(T, int) R) []R {
	result := make([]R, len(items))
	for i, v := range items {
		result[i] = fn(v, i)
	}
	return result
}
