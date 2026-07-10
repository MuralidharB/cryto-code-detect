package indirect

import (
	"crypto"
	"crypto/ed25519"
	"crypto/rand"
)

func newSigner() (crypto.Signer, error) {
	_, priv, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		return nil, err
	}
	return priv, nil
}

func SignMessage(message []byte) ([]byte, crypto.PublicKey, error) {
	signer, err := newSigner()
	if err != nil {
		return nil, nil, err
	}
	sig, err := signer.Sign(rand.Reader, message, crypto.Hash(0))
	if err != nil {
		return nil, nil, err
	}
	return sig, signer.Public(), nil
}

func Verify(pub crypto.PublicKey, message, sig []byte) bool {
	return ed25519.Verify(pub.(ed25519.PublicKey), message, sig)
}
