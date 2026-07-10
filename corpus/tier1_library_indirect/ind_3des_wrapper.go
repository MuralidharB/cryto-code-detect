package indirect

import (
	"crypto/cipher"
	"crypto/des"
)

type blockFactory func(key []byte) (cipher.Block, error)

func tripleDESFactory() blockFactory {
	return func(key []byte) (cipher.Block, error) {
		return des.NewTripleDESCipher(key)
	}
}

func EncryptECB(key, plaintext []byte) ([]byte, error) {
	block, err := tripleDESFactory()(key)
	if err != nil {
		return nil, err
	}
	bs := block.BlockSize()
	out := make([]byte, len(plaintext))
	for i := 0; i < len(plaintext); i += bs {
		block.Encrypt(out[i:i+bs], plaintext[i:i+bs])
	}
	return out, nil
}
