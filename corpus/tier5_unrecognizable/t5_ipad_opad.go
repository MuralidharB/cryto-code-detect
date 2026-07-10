package t5

// HashFn reduces an arbitrary message to a fixed-length tag.
type HashFn func(msg []byte) []byte

const blockLen = 64

func padKey(key []byte, hash HashFn) []byte {
	k := key
	if len(k) > blockLen {
		k = hash(k)
	}
	out := make([]byte, blockLen)
	copy(out, k)
	return out
}

func xorConst(k []byte, c byte) []byte {
	out := make([]byte, len(k))
	for i := range k {
		out[i] = k[i] ^ c
	}
	return out
}

// Authenticate binds key and message using two nested passes of hash with
// two derived key pads (inner 0x36, outer 0x5c).
func Authenticate(key, msg []byte, hash HashFn) []byte {
	k := padKey(key, hash)
	inner := append(xorConst(k, 0x36), msg...)
	innerTag := hash(inner)
	outer := append(xorConst(k, 0x5c), innerTag...)
	return hash(outer)
}
