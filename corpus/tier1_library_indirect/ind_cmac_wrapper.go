package indirect

import (
	"crypto/aes"

	"github.com/aead/cmac"
)

type macFn func(key, msg []byte) ([]byte, error)

func cmacOver(key, msg []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	return cmac.Sum(msg, block, block.BlockSize())
}

type Authenticator struct {
	compute macFn
}

func NewAuthenticator() *Authenticator {
	return &Authenticator{compute: cmacOver}
}

func (a *Authenticator) Tag(key, msg []byte) ([]byte, error) {
	return a.compute(key, msg)
}
