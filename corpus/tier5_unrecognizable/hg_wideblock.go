package main

const bs = 1024

func subTable(key []byte) ([256]byte, [256]byte) {
	var f [256]byte
	for i := range f {
		f[i] = byte(i)
	}
	j := 0
	for r := 0; r < 3; r++ {
		for i := 0; i < 256; i++ {
			j = (j + int(f[i]) + int(key[i%len(key)]) + r) & 0xFF
			f[i], f[j] = f[j], f[i]
		}
	}
	var inv [256]byte
	for i, v := range f {
		inv[v] = byte(i)
	}
	return f, inv
}

// reversible linear mixing pass over disjoint pairs of 16-bit words
func phtForward(b []byte) {
	for i := 0; i+3 < len(b); i += 4 {
		a := uint16(b[i])<<8 | uint16(b[i+1])
		c := uint16(b[i+2])<<8 | uint16(b[i+3])
		na := a + c
		nc := a + 2*c
		b[i], b[i+1] = byte(na>>8), byte(na)
		b[i+2], b[i+3] = byte(nc>>8), byte(nc)
	}
}

func phtBackward(b []byte) {
	for i := 0; i+3 < len(b); i += 4 {
		na := uint16(b[i])<<8 | uint16(b[i+1])
		nc := uint16(b[i+2])<<8 | uint16(b[i+3])
		c := nc - na
		a := na - c
		b[i], b[i+1] = byte(a>>8), byte(a)
		b[i+2], b[i+3] = byte(c>>8), byte(c)
	}
}

func forward(b []byte, key []byte) {
	f, _ := subTable(key)
	phtForward(b)
	for i := range b {
		b[i] = f[b[i]]
	}
}

func backward(b []byte, key []byte) {
	_, inv := subTable(key)
	for i := range b {
		b[i] = inv[b[i]]
	}
	phtBackward(b)
}

func main() {
	key := []byte("wide-key-01")
	b := make([]byte, bs)
	orig := make([]byte, bs)
	for i := range b {
		b[i] = byte(i * 7)
		orig[i] = b[i]
	}
	forward(b, key)
	backward(b, key)
	for i := range b {
		if b[i] != orig[i] {
			panic("mismatch")
		}
	}
}
