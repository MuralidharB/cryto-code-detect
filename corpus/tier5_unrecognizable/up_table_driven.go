package main

import "fmt"

// Processes eight independent lanes in parallel through precomputed,
// argument-dependent lookup tables. Each lane owns its own 256-entry table
// derived from the argument, giving a wide table-driven byte transform.

type engine struct {
	tables [8][256]byte
}

func newEngine(param []byte) *engine {
	e := &engine{}
	for lane := 0; lane < 8; lane++ {
		seed := uint32(lane*2654435761 + 1)
		for _, pb := range param {
			seed = seed*16777619 ^ uint32(pb)
		}
		// build a bijection of 0..255 by an argument-driven swap walk
		var t [256]byte
		for i := 0; i < 256; i++ {
			t[i] = byte(i)
		}
		j := byte(0)
		for i := 0; i < 256; i++ {
			seed = seed*1103515245 + 12345
			j += byte(seed>>16) + t[i] + param[i%len(param)]
			t[i], t[j] = t[j], t[i]
		}
		e.tables[lane] = t
	}
	return e
}

// forward maps a group of up to 8 bytes, one lane per byte.
func (e *engine) forward(group []byte) []byte {
	out := make([]byte, len(group))
	for i := range group {
		out[i] = e.tables[i&7][group[i]]
	}
	return out
}

// inverse rebuilds the reverse tables and undoes forward.
func (e *engine) inverse(group []byte) []byte {
	var inv [8][256]byte
	for lane := 0; lane < 8; lane++ {
		for i := 0; i < 256; i++ {
			inv[lane][e.tables[lane][i]] = byte(i)
		}
	}
	out := make([]byte, len(group))
	for i := range group {
		out[i] = inv[i&7][group[i]]
	}
	return out
}

func main() {
	e := newEngine([]byte("lane-arg-42"))
	msg := []byte{10, 20, 30, 40, 50, 60, 70, 80}
	enc := e.forward(msg)
	dec := e.inverse(enc)
	fmt.Printf("%x %v\n", enc, string(dec) == string(msg))
}
