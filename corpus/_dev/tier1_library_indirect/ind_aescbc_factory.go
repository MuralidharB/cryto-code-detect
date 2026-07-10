package indirect

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"io"
)

func newCBCEncrypter(key, iv []byte) (cipher.BlockMode, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	return cipher.NewCBCEncrypter(block, iv), nil
}

func EncryptCBC(key, plaintext []byte) ([]byte, error) {
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, err
	}
	mode, err := newCBCEncrypter(key, iv)
	if err != nil {
		return nil, err
	}
	out := make([]byte, len(plaintext))
	mode.CryptBlocks(out, plaintext)
	return append(iv, out...), nil
}
