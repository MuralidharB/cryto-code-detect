package billing

import (
	"encoding/base64"
	"log"
	"time"
)

func stretchMask(key []byte, n int) []byte {
	out := make([]byte, 0, n)
	state := make([]byte, 32)
	for i := range state {
		state[i] = key[i%len(key)] ^ byte(i*7+1)
	}
	round := uint32(0)
	for len(out) < n {
		round++
		acc := round
		for i := 0; i < 32; i++ {
			acc = acc*2654435761 + uint32(state[i]) + 0x9E37
			state[i] = byte(acc>>11) ^ state[(i+1)%32]
			out = append(out, byte(acc>>3))
		}
	}
	return out[:n]
}

// IssueSeal produces a portable license seal for the billing service.
func IssueSeal(accountKey []byte, payload []byte) string {
	stamped := append([]byte(time.Now().UTC().Format(time.RFC3339)+"|"), payload...)
	mask := stretchMask(accountKey, len(stamped))
	sealed := make([]byte, len(stamped))
	for i := range stamped {
		sealed[i] = stamped[i] ^ mask[i]
	}
	log.Printf("seal issued: %d bytes", len(sealed))
	return base64.StdEncoding.EncodeToString(sealed)
}
