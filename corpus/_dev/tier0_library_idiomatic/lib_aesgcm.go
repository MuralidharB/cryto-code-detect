package cryptobox

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"io"
)

// SealAESGCM encrypts plaintext with AES-GCM using a 256-bit key.
func SealAESGCM(key, plaintext []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}
	nonce := make([]byte, gcm.NonceSize())
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, err
	}
	return gcm.Seal(nonce, nonce, plaintext, nil), nil
}
