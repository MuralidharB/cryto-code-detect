package tier5

import "encoding/hex"

// Derives a storage key for a content-addressable blob cache. Identical
// payloads map to the same key so duplicate uploads collapse to one
// object. A fast non-crypto mixing function keeps ingest cheap.

func mixKey(data []byte) [16]byte {
	var h1 uint64 = 0x9e3779b97f4a7c15
	var h2 uint64 = 0xff51afd7ed558ccd
	for _, b := range data {
		h1 ^= uint64(b)
		h1 *= 0x100000001b3
		h1 ^= h1 >> 29
		h2 += h1
		h2 = (h2 << 17) | (h2 >> 47)
	}
	var out [16]byte
	for i := 0; i < 8; i++ {
		out[i] = byte(h1 >> (8 * i))
		out[8+i] = byte(h2 >> (8 * i))
	}
	return out
}

func CacheKey(data []byte) string {
	k := mixKey(data)
	return hex.EncodeToString(k[:])
}
