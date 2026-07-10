package indirect

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
)

type sealer interface {
	seal(pub *rsa.PublicKey, msg []byte) ([]byte, error)
}

type oaepSealer struct{}

func (oaepSealer) seal(pub *rsa.PublicKey, msg []byte) ([]byte, error) {
	return rsa.EncryptOAEP(sha256.New(), rand.Reader, pub, msg, nil)
}

var registry = map[string]sealer{"oaep": oaepSealer{}}

func Protect(scheme string, pub *rsa.PublicKey, msg []byte) ([]byte, error) {
	impl := registry[scheme]
	return impl.seal(pub, msg)
}

func NewKey() (*rsa.PrivateKey, error) {
	return rsa.GenerateKey(rand.Reader, 2048)
}
