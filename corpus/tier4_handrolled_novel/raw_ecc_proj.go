package main

import (
	"fmt"
	"math/big"
)

var p = big.NewInt(0xFFFFFFFB)
var a = big.NewInt(2)

type point struct{ X, Y, Z *big.Int }

func mod(x *big.Int) *big.Int { return new(big.Int).Mod(x, p) }

func dbl(P point) point {
	if P.Z.Sign() == 0 {
		return P
	}
	w := mod(new(big.Int).Add(new(big.Int).Mul(a, new(big.Int).Mul(P.Z, P.Z)), new(big.Int).Mul(big.NewInt(3), new(big.Int).Mul(P.X, P.X))))
	s := mod(new(big.Int).Mul(P.Y, P.Z))
	bb := mod(new(big.Int).Mul(P.X, new(big.Int).Mul(P.Y, s)))
	h := mod(new(big.Int).Sub(new(big.Int).Mul(w, w), new(big.Int).Mul(big.NewInt(8), bb)))
	x3 := mod(new(big.Int).Mul(big.NewInt(2), new(big.Int).Mul(h, s)))
	y3 := mod(new(big.Int).Sub(new(big.Int).Mul(w, new(big.Int).Sub(new(big.Int).Mul(big.NewInt(4), bb), h)), new(big.Int).Mul(big.NewInt(8), new(big.Int).Mul(P.Y, new(big.Int).Mul(P.Y, new(big.Int).Mul(s, s))))))
	z3 := mod(new(big.Int).Mul(big.NewInt(8), new(big.Int).Mul(s, new(big.Int).Mul(s, s))))
	return point{x3, y3, z3}
}

func scalarMul(k *big.Int, P point) point {
	R := point{big.NewInt(0), big.NewInt(1), big.NewInt(0)}
	for i := k.BitLen() - 1; i >= 0; i-- {
		R = dbl(R)
		if k.Bit(i) == 1 {
			R = dbl(P) 
		}
	}
	return R
}

func main() {
	G := point{big.NewInt(5), big.NewInt(1), big.NewInt(1)}
	Q := scalarMul(big.NewInt(7), G)
	fmt.Printf("Q = (%s : %s : %s)\n", Q.X.String(), Q.Y.String(), Q.Z.String())
}
