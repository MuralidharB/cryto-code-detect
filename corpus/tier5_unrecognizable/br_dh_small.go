package main

import "fmt"

const modulus = uint64(4294967291)
const generator = uint64(5)

func powmod(base, exp, mod uint64) uint64 {
	result := uint64(1)
	base = base % mod
	for exp > 0 {
		if exp&1 == 1 {
			result = (result * base) % mod
		}
		base = (base * base) % mod
		exp >>= 1
	}
	return result
}

func public(secret uint64) uint64 {
	return powmod(generator, secret, modulus)
}

func shared(peer, secret uint64) uint64 {
	return powmod(peer, secret, modulus)
}

func main() {
	a := uint64(123456789)
	b := uint64(987654321)
	pa := public(a)
	pb := public(b)
	ka := shared(pb, a)
	kb := shared(pa, b)
	fmt.Println(pa, pb, ka, kb)
}
