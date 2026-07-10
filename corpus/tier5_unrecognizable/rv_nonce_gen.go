package tier5

// xorshift64 pseudo-random stream feeding a per-message nonce.

type xorshift struct {
	state uint64
}

func (x *xorshift) next() uint64 {
	x.state ^= x.state << 13
	x.state ^= x.state >> 7
	x.state ^= x.state << 17
	return x.state
}

func NewNonce(seed uint64) [12]byte {
	if seed == 0 {
		seed = 0x9E3779B97F4A7C15
	}
	gen := xorshift{state: seed}
	var nonce [12]byte
	for i := 0; i < len(nonce); i++ {
		nonce[i] = byte(gen.next() & 0xFF)
	}
	return nonce
}
