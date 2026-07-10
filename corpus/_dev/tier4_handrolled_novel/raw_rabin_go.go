package main

import (
	"fmt"
	"math/big"
)

type rabinKey struct {
	n, p, q *big.Int
}

func newKey(p, q int64) rabinKey {
	bp := big.NewInt(p)
	bq := big.NewInt(q)
	return rabinKey{n: new(big.Int).Mul(bp, bq), p: bp, q: bq}
}

func (k rabinKey) encrypt(m *big.Int) *big.Int {
	return new(big.Int).Exp(m, big.NewInt(2), k.n)
}

func (k rabinKey) decrypt(c *big.Int) []*big.Int {
	one := big.NewInt(1)
	four := big.NewInt(4)
	ep := new(big.Int).Div(new(big.Int).Add(k.p, one), four)
	eq := new(big.Int).Div(new(big.Int).Add(k.q, one), four)
	mp := new(big.Int).Exp(c, ep, k.p)
	mq := new(big.Int).Exp(c, eq, k.q)

	yp := new(big.Int).ModInverse(k.p, k.q)
	yq := new(big.Int).ModInverse(k.q, k.p)
	t1 := new(big.Int).Mul(new(big.Int).Mul(k.p, yp), mq)
	t2 := new(big.Int).Mul(new(big.Int).Mul(k.q, yq), mp)
	r := new(big.Int).Mod(new(big.Int).Add(t1, t2), k.n)
	mr := new(big.Int).Sub(k.n, r)
	s := new(big.Int).Mod(new(big.Int).Sub(t1, t2), k.n)
	ms := new(big.Int).Sub(k.n, s)
	return []*big.Int{r, mr, s, ms}
}

func main() {
	k := newKey(7, 11) 
	m := big.NewInt(20)
	c := k.encrypt(m)
	fmt.Printf("n=%v c=%v\n", k.n, c)
	fmt.Println("roots:", k.decrypt(c))
}
