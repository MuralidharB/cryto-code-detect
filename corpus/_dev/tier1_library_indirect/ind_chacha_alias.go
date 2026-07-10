package indirect

import (
	"crypto/rand"
	"io"

	stream "golang.org/x/crypto/chacha20"
)

func buildStream(key, nonce []byte) (*stream.Cipher, error) {
	return stream.NewUnauthenticatedCipher(key, nonce)
}

func XOREncrypt(key, plaintext []byte) ([]byte, error) {
	nonce := make([]byte, stream.NonceSize)
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, err
	}
	c, err := buildStream(key, nonce)
	if err != nil {
		return nil, err
	}
	out := make([]byte, len(plaintext))
	c.XORKeyStream(out, plaintext)
	return append(nonce, out...), nil
}
