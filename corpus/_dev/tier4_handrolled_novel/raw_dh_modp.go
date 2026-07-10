package main

import (
	"fmt"
	"math/big"
)

func modPow(base, exp, mod *big.Int) *big.Int {
	return new(big.Int).Exp(base, exp, mod)
}

func main() {
	p, _ := new(big.Int).SetString("FFFFFFFFFFFFFFC5", 16)
	g := big.NewInt(5)

	a := big.NewInt(0x1A2B3C4D)
	b := big.NewInt(0x5E6F7A8B)

	A := modPow(g, a, p)
	B := modPow(g, b, p)

	sharedA := modPow(B, a, p)
	sharedB := modPow(A, b, p)

	fmt.Printf("A pub : %s\n", A.String())
	fmt.Printf("B pub : %s\n", B.String())
	fmt.Printf("shared: %s == %s\n", sharedA.String(), sharedB.String())
	if sharedA.Cmp(sharedB) != 0 {
		panic("shared secret mismatch")
	}
}
