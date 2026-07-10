package indirect

import (
	"crypto/sha256"
	"hash"
	"io"

	"golang.org/x/crypto/hkdf"
)

func deriver(secret, salt, info []byte) io.Reader {
	var h func() hash.Hash = sha256.New
	return hkdf.New(h, secret, salt, info)
}

func DeriveKey(secret, salt, info []byte, length int) ([]byte, error) {
	r := deriver(secret, salt, info)
	out := make([]byte, length)
	if _, err := io.ReadFull(r, out); err != nil {
		return nil, err
	}
	return out, nil
}
