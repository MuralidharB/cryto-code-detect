package crypteng

import (
	"crypto/aes"
	"crypto/cipher"
	"fmt"
)

func newBlock(key []byte) cipher.Block {
	b, err := aes.NewCipher(key)
	if err != nil {
		panic(fmt.Sprintf("invalid key: %v", err))
	}
	return b
}

func newStream(key, iv []byte) cipher.Stream {
	return cipher.NewCTR(newBlock(key), iv)
}

func Transform(key, iv, data []byte) []byte {
	out := make([]byte, len(data))
	newStream(key, iv).XORKeyStream(out, data)
	return out
}

func BlockSize(key []byte) int {
	return newBlock(key).BlockSize()
}
