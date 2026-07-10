package stream

import "crypto/rc4"

// EncryptRC4 applies the RC4 stream cipher to data using key.
func EncryptRC4(key, data []byte) ([]byte, error) {
	c, err := rc4.NewCipher(key)
	if err != nil {
		return nil, err
	}
	out := make([]byte, len(data))
	c.XORKeyStream(out, data)
	return out, nil
}
