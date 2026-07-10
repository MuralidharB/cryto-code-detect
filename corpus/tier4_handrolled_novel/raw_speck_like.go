package main

import "fmt"

func rotr(x uint32, r uint) uint32 { return (x >> r) | (x << (32 - r)) }
func rotl(x uint32, r uint) uint32 { return (x << r) | (x >> (32 - r)) }

func round(x, y, k uint32) (uint32, uint32) {
	x = rotr(x, 8)
	x += y
	x ^= k
	y = rotl(y, 3)
	y ^= x
	return x, y
}

func encrypt(x, y uint32, key []uint32) (uint32, uint32) {
	for _, k := range key {
		x, y = round(x, y, k)
	}
	return x, y
}

func keySchedule(k0, k1 uint32, rounds int) []uint32 {
	ks := make([]uint32, rounds)
	a, b := k0, k1
	for i := 0; i < rounds; i++ {
		ks[i] = a
		b, a = round(b, a, uint32(i))
	}
	return ks
}

func main() {
	keys := keySchedule(0x01234567, 0x89abcdef, 27)
	cx, cy := encrypt(0xdeadbeef, 0x0badf00d, keys)
	fmt.Printf("blk: %08x %08x\n", cx, cy)
}
