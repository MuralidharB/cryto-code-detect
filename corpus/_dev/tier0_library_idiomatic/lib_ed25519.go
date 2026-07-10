package signer

import (
	"crypto/ed25519"
	"crypto/rand"
)

// SignEd25519 generates an Ed25519 keypair and signs message.
func SignEd25519(message []byte) ([]byte, error) {
	_, priv, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		return nil, err
	}
	return ed25519.Sign(priv, message), nil
}
