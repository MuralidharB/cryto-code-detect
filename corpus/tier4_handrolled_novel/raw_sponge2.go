package main

import "fmt"

const (
	stateLen = 8 
	rate     = 4
)

func permute(s []uint64) {
	for r := 0; r < 12; r++ {
		for i := 0; i < stateLen; i++ {
			s[i] += s[(i+1)%stateLen]
			s[i] = (s[i] << 13) | (s[i] >> 51)
			s[i] ^= s[(i+3)%stateLen]
			s[i] += uint64(r)*0x9E3779B97F4A7C15 + uint64(i)
		}
	}
}

func sponge(msg []uint64) []uint64 {
	state := make([]uint64, stateLen)
	for i := 0; i < len(msg); i += rate {
		for j := 0; j < rate && i+j < len(msg); j++ {
			state[j] ^= msg[i+j]
		}
		permute(state)
	}
	permute(state)
	return state[:rate]
}

func main() {
	msg := []uint64{0x0102030405060708, 0x1112131415161718, 0xdeadbeefcafebabe}
	digest := sponge(msg)
	fmt.Printf("blk: %016x %016x %016x %016x\n", digest[0], digest[1], digest[2], digest[3])
}
