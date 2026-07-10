package main

import "fmt"

func rotl32(x, n uint32) uint32 {
	return (x << n) | (x >> (32 - n))
}

func roundFn(half, rk uint32) uint32 {
	v := half + rk
	v = rotl32(v, 7)
	v ^= rotl32(v, 13)
	v = v + (v << 3)
	return v ^ rk
}

func feistelEncrypt(block uint64, key uint64) uint64 {
	left := uint32(block >> 32)
	right := uint32(block & 0xffffffff)
	subkeys := [4]uint32{}
	for i := 0; i < 4; i++ {
		subkeys[i] = uint32(key>>uint(8*i)) ^ (0x9e3779b9 * uint32(i+1))
	}
	for r := 0; r < 4; r++ {
		next := left ^ roundFn(right, subkeys[r])
		left = right
		right = next
	}
	return (uint64(left) << 32) | uint64(right)
}

func feistelDecrypt(block uint64, key uint64) uint64 {
	left := uint32(block >> 32)
	right := uint32(block & 0xffffffff)
	subkeys := [4]uint32{}
	for i := 0; i < 4; i++ {
		subkeys[i] = uint32(key>>uint(8*i)) ^ (0x9e3779b9 * uint32(i+1))
	}
	for r := 3; r >= 0; r-- {
		prev := right ^ roundFn(left, subkeys[r])
		right = left
		left = prev
	}
	return (uint64(left) << 32) | uint64(right)
}

func main() {
	pt := uint64(0x0123456789abcdef)
	key := uint64(0xdeadbeefcafef00d)
	ct := feistelEncrypt(pt, key)
	rt := feistelDecrypt(ct, key)
	fmt.Printf("pt=%016x ct=%016x rt=%016x\n", pt, ct, rt)
}
