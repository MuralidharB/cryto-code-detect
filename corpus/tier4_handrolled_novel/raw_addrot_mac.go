package main

import "fmt"

func rotl64(x uint64, r uint) uint64 { return (x << r) | (x >> (64 - r)) }

func mac(key0, key1 uint64, msg []byte) uint64 {
	a := key0
	b := key1 ^ 0xA5A5A5A5A5A5A5A5
	for i, by := range msg {
		a += uint64(by) + uint64(i)
		a = rotl64(a, 17)
		a ^= b
		b += a
		b = rotl64(b, 41)
	}
	a ^= rotl64(b, 23)
	a += key0
	a = rotl64(a, 32) ^ b
	return a
}

func main() {
	tag := mac(0x0123456789abcdef, 0xfedcba9876543210, []byte("authenticate me"))
	fmt.Printf("tag: %016x\n", tag)
}
