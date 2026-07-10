package signing

import (
	"crypto"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
)

func loadSigner() (crypto.Signer, error) {
	priv, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return nil, err
	}
	return priv, nil
}

func Attest(digest []byte) ([]byte, crypto.PublicKey, error) {
	s, err := loadSigner()
	if err != nil {
		return nil, nil, err
	}
	sig, err := s.Sign(rand.Reader, digest, crypto.SHA256)
	if err != nil {
		return nil, nil, err
	}
	return sig, s.Public(), nil
}
