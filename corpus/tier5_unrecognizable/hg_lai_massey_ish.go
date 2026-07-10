package main

func rotl(v uint32, n uint) uint32 {
	return (v << n) | (v >> (32 - n))
}

func ortho(x uint32) uint32 {
	// bijective nonlinear map used both ways via its structure
	x = x*0x9E3779B1 + 0x7F4A7C15
	x ^= rotl(x, 13)
	return x + rotl(x, 7)
}

func subkeys(key uint64) [8]uint32 {
	var sk [8]uint32
	s := key ^ 0xA0761D6478BD642F
	for i := 0; i < 8; i++ {
		s ^= s << 12
		s ^= s >> 25
		s ^= s << 27
		sk[i] = uint32(s * 0x2545F4914F6CDD1D >> 32)
	}
	return sk
}

func forward(l, r uint32, key uint64) (uint32, uint32) {
	sk := subkeys(key)
	for i := 0; i < 8; i++ {
		d := l - r
		t := ortho(d ^ sk[i])
		l = (l + t) ^ rotl(sk[i], 5)
		r = (r + t) ^ rotl(sk[i], 11)
	}
	return l, r
}

func backward(l, r uint32, key uint64) (uint32, uint32) {
	sk := subkeys(key)
	for i := 7; i >= 0; i-- {
		lp := l ^ rotl(sk[i], 5)
		rp := r ^ rotl(sk[i], 11)
		d := lp - rp
		t := ortho(d ^ sk[i])
		l = lp - t
		r = rp - t
	}
	return l, r
}

func main() {
	l, r := uint32(0xDEADBEEF), uint32(0x01234567)
	el, er := forward(l, r, 0xF00DCAFE)
	dl, dr := backward(el, er, 0xF00DCAFE)
	if dl != l || dr != r {
		panic("mismatch")
	}
}
