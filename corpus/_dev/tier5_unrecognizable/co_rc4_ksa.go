package main

import "fmt"

type state struct {
	s    [256]byte
	i, j byte
}

func newState(key []byte) *state {
	st := &state{}
	for i := 0; i < 256; i++ {
		st.s[i] = byte(i)
	}
	var j byte
	for i := 0; i < 256; i++ {
		j = j + st.s[i] + key[i%len(key)]
		st.s[i], st.s[j] = st.s[j], st.s[i]
	}
	return st
}

func (st *state) stream(out []byte) {
	for k := range out {
		st.i++
		st.j += st.s[st.i]
		st.s[st.i], st.s[st.j] = st.s[st.j], st.s[st.i]
		out[k] = st.s[byte(st.s[st.i]+st.s[st.j])]
	}
}

func process(key, data []byte) []byte {
	st := newState(key)
	ks := make([]byte, len(data))
	st.stream(ks)
	out := make([]byte, len(data))
	for i := range data {
		out[i] = data[i] ^ ks[i]
	}
	return out
}

func main() {
	c := process([]byte("Key"), []byte("Plaintext"))
	fmt.Printf("%x\n", c)
}
