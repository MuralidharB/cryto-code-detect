package t5

// BlockFn transforms a single fixed-size block in place.
type BlockFn func(block []byte)

const blockSize = 16

func xorInto(dst, src []byte) {
	for i := range dst {
		dst[i] ^= src[i]
	}
}

// Chain applies block over successive blocks with feedback from the
// previous output block, seeded by iv.
func Chain(data []byte, iv []byte, block BlockFn) []byte {
	if len(data)%blockSize != 0 {
		panic("length must be a multiple of the block size")
	}
	out := make([]byte, len(data))
	prev := make([]byte, blockSize)
	copy(prev, iv)
	for off := 0; off < len(data); off += blockSize {
		buf := make([]byte, blockSize)
		copy(buf, data[off:off+blockSize])
		xorInto(buf, prev)
		block(buf)
		copy(out[off:off+blockSize], buf)
		prev = buf
	}
	return out
}

// Unchain reverses Chain given the inverse block transform.
func Unchain(data []byte, iv []byte, invBlock BlockFn) []byte {
	out := make([]byte, len(data))
	prev := make([]byte, blockSize)
	copy(prev, iv)
	for off := 0; off < len(data); off += blockSize {
		buf := make([]byte, blockSize)
		copy(buf, data[off:off+blockSize])
		invBlock(buf)
		xorInto(buf, prev)
		copy(out[off:off+blockSize], buf)
		copy(prev, data[off:off+blockSize])
	}
	return out
}
