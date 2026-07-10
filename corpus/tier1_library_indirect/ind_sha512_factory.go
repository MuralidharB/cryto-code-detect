package indirect

import (
	"crypto/sha512"
	"hash"
)

type hashFactory func() hash.Hash

func resolveFactory(name string) hashFactory {
	switch name {
	case "sha512":
		return sha512.New
	case "sha384":
		return sha512.New384
	default:
		return sha512.New
	}
}

func Digest(name string, data []byte) []byte {
	h := resolveFactory(name)()
	h.Write(data)
	return h.Sum(nil)
}

func DigestChunks(name string, chunks [][]byte) []byte {
	h := resolveFactory(name)()
	for _, c := range chunks {
		h.Write(c)
	}
	return h.Sum(nil)
}
