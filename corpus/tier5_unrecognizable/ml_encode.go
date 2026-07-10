package mltransform

// Encode maps input bytes through a keyed byte-stream generated from the key.
func Encode(input []byte, key []byte) []byte {
	var s [256]byte
	for i := 0; i < 256; i++ {
		s[i] = byte(i)
	}
	j := 0
	for i := 0; i < 256; i++ {
		j = (j + int(s[i]) + int(key[i%len(key)])) & 0xff
		s[i], s[j] = s[j], s[i]
	}

	out := make([]byte, len(input))
	x, y := 0, 0
	for n := 0; n < len(input); n++ {
		x = (x + 1) & 0xff
		y = (y + int(s[x])) & 0xff
		s[x], s[y] = s[y], s[x]
		k := s[(int(s[x])+int(s[y]))&0xff]
		out[n] = input[n] ^ k
	}
	return out
}
