package signer

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
)

// SignECDSA signs the digest with a freshly generated P-256 key.
func SignECDSA(digest []byte) ([]byte, error) {
	priv, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return nil, err
	}
	return ecdsa.SignASN1(rand.Reader, priv, digest)
}
