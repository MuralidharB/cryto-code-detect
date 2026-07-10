package main

import "fmt"

type lfsr struct {
	state uint16
}

func (l *lfsr) next() uint8 {
	var out uint8
	for i := 0; i < 8; i++ {
		bit := (l.state ^ (l.state >> 2) ^ (l.state >> 3) ^ (l.state >> 5)) & 1
		l.state = (l.state >> 1) | (bit << 15)
		out = (out << 1) | uint8(l.state&1)
	}
	return out
}

func crypt(seed uint16, data []byte) []byte {
	l := &lfsr{state: seed}
	out := make([]byte, len(data))
	for i, b := range data {
		out[i] = b ^ l.next()
	}
	return out
}

func main() {
	msg := []byte("hello blk world")
	ct := crypt(0xACE1, msg)
	pt := crypt(0xACE1, ct)
	fmt.Printf("blk: %x\n", ct)
	fmt.Printf("plain : %s\n", string(pt))
}
