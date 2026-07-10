package main

import (
	"fmt"
	"math/big"
)

func lFunc(x, n *big.Int) *big.Int {
	num := new(big.Int).Sub(x, big.NewInt(1))
	return new(big.Int).Div(num, n)
}

func encrypt(m, g, n, n2, r *big.Int) *big.Int {
	gm := new(big.Int).Exp(g, m, n2)
	rn := new(big.Int).Exp(r, n, n2)
	c := new(big.Int).Mul(gm, rn)
	return c.Mod(c, n2)
}

func decrypt(c, lambda, mu, n, n2 *big.Int) *big.Int {
	u := new(big.Int).Exp(c, lambda, n2)
	m := new(big.Int).Mul(lFunc(u, n), mu)
	return m.Mod(m, n)
}

func main() {
	p := big.NewInt(1019)
	q := big.NewInt(1031)
	n := new(big.Int).Mul(p, q)
	n2 := new(big.Int).Mul(n, n)
	g := new(big.Int).Add(n, big.NewInt(1))
	lambda := new(big.Int).Mul(new(big.Int).Sub(p, big.NewInt(1)), new(big.Int).Sub(q, big.NewInt(1)))
	mu := new(big.Int).ModInverse(lFunc(new(big.Int).Exp(g, lambda, n2), n), n)

	m := big.NewInt(424242)
	r := big.NewInt(7919)
	c := encrypt(m, g, n, n2, r)
	d := decrypt(c, lambda, mu, n, n2)
	fmt.Printf("blk: %s\ndecrypt: %s\n", c.String(), d.String())
}
