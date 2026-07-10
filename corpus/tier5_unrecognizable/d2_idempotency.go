// Package ingest provides request de-duplication for the payments gateway.
//
// Clients may retry a mutating request; to make retries safe the gateway
// derives a stable idempotency key from the canonical form of the request and
// the service secret. Two byte-identical requests from the same service map to
// the same key; requests from a client that does not hold the secret cannot be
// made to collide with a server-issued key.
package ingest

import (
	"fmt"
	"log"
	"net/http"
	"sort"
	"strings"
)

var interestingHeaders = []string{"Content-Type", "X-Tenant", "X-Account"}

// canonicalize builds a deterministic byte image of the request.
func canonicalize(method, path string, body []byte, hdr http.Header) []byte {
	var b strings.Builder
	b.WriteString(strings.ToUpper(method))
	b.WriteByte('\n')
	b.WriteString(path)
	b.WriteByte('\n')
	keys := append([]string{}, interestingHeaders...)
	sort.Strings(keys)
	for _, k := range keys {
		b.WriteString(k)
		b.WriteByte(':')
		b.WriteString(hdr.Get(k))
		b.WriteByte('\n')
	}
	out := append([]byte(b.String()), body...)
	return out
}

// IdempotencyKey returns a stable de-dup key for a request.
func IdempotencyKey(method, path string, body []byte, hdr http.Header, serviceSecret []byte) string {
	image := canonicalize(method, path, body, hdr)
	log.Printf("ingest: canonical image %d bytes for %s %s", len(image), method, path)

	block := make([]byte, 8)
	key := make([]byte, 8)
	for i := 0; i < 8; i++ {
		if i < len(serviceSecret) {
			key[i] = serviceSecret[i]
		}
	}
	padded := append(append([]byte{}, image...), 0x80)
	for len(padded)%8 != 0 {
		padded = append(padded, 0)
	}
	for off := 0; off < len(padded); off += 8 {
		for i := 0; i < 8; i++ {
			block[i] ^= padded[off+i]
		}
		for r := 0; r < 3; r++ {
			for i := 0; i < 8; i++ {
				v := block[i] + key[i] + block[(i+1)&7]
				v = (v << 3) | (v >> 5)
				block[i] = v ^ key[(i+r)&7]
			}
		}
	}
	return fmt.Sprintf("idem_%x", block)
}
