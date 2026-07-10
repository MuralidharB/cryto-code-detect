package main

type walker struct {
	tab  [256]byte
	a, b int
	acc  byte
}

func newWalker(key []byte) *walker {
	w := &walker{}
	for i := range w.tab {
		w.tab[i] = byte(i)
	}
	j := 0
	for round := 0; round < 3; round++ {
		for i := 0; i < 256; i++ {
			j = (j + int(w.tab[i]) + int(key[i%len(key)]) + round) & 0xFF
			w.tab[i], w.tab[j] = w.tab[j], w.tab[i]
		}
	}
	return w
}

func (w *walker) next() byte {
	w.a = (w.a + 1) & 0xFF
	w.b = (w.b + int(w.tab[w.a]) + int(w.acc)) & 0xFF
	w.tab[w.a], w.tab[w.b] = w.tab[w.b], w.tab[w.a]
	idx := (int(w.tab[w.a]) + int(w.tab[w.b])) & 0xFF
	out := w.tab[idx] ^ ((w.acc << 3) | (w.acc >> 5))
	w.acc = out
	return out
}

func apply(data, key []byte) []byte {
	w := newWalker(key)
	out := make([]byte, len(data))
	for i, c := range data {
		out[i] = c ^ w.next()
	}
	return out
}

func main() {
	key := []byte("sample-key-1234")
	msg := []byte("stream over a keyed permutation walk")
	ct := apply(msg, key)
	pt := apply(ct, key)
	for i := range msg {
		if pt[i] != msg[i] {
			panic("mismatch")
		}
	}
}
