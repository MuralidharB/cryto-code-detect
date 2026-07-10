package split

const blockLen = 16

func shuffle(block []byte) []byte {
	out := make([]byte, blockLen)
	for i := 0; i < blockLen; i++ {
		src := (i*7 + 3) % blockLen
		v := block[src]
		v = (v << 3) | (v >> 5)
		out[i] = v
	}
	return out
}
