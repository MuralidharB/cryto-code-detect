package main

import "fmt"

const (
	fnvOffset uint64 = 14695981039346656037
	fnvPrime  uint64 = 1099511628211
)

func fnv1a(data []byte) uint64 {
	h := fnvOffset
	for _, b := range data {
		h ^= uint64(b)
		h *= fnvPrime
	}
	return h
}

func bucketIndex(key string, buckets uint64) uint64 {
	return fnv1a([]byte(key)) % buckets
}

func main() {
	fmt.Printf("%016x\n", fnv1a([]byte("hash table key")))
	fmt.Println(bucketIndex("another key", 256))
}
