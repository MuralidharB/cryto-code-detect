package indirect

import (
	hashlib "golang.org/x/crypto/sha3"
)

type digester func([]byte) [32]byte

func newDigester() digester {
	return hashlib.Sum256
}

func Checksum(data []byte) []byte {
	fn := newDigester()
	out := fn(data)
	return out[:]
}
