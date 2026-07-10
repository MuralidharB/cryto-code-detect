package keys

import (
	"crypto/rand"
	"crypto/rsa"
)

// NewRSAKey generates a fresh 2048-bit RSA private key.
func NewRSAKey() (*rsa.PrivateKey, error) {
	priv, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return nil, err
	}
	return priv, nil
}
