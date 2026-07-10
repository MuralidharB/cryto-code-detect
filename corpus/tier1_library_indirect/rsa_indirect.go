package keys

import (
	rsalib "crypto/rsa"
	crand "crypto/rand"
	"fmt"
	"io"
)

type Generator struct {
	bits   int
	source io.Reader
}

func NewGenerator(bits int) *Generator {
	return &Generator{bits: bits, source: crand.Reader}
}

func (g *Generator) make() (*rsalib.PrivateKey, error) {
	return rsalib.GenerateKey(g.source, g.bits)
}

func Provision(bits int) (*rsalib.PrivateKey, error) {
	g := NewGenerator(bits)
	k, err := g.make()
	if err != nil {
		return nil, fmt.Errorf("provision: %w", err)
	}
	return k, nil
}

func PublicOf(k *rsalib.PrivateKey) *rsalib.PublicKey {
	return &k.PublicKey
}
