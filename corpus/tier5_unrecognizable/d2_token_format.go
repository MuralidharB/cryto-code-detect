// Package sessionfmt formats session tokens for the edge tier.
//
// A session token carries a few claims (subject, tenant, expiry). Before the
// claims are framed for the wire they are run through a keyed reversible mixing
// pass so that the token is opaque to the client and cannot be edited to change
// claims without the edge secret; the reader tier reverses the pass to recover
// the claim bytes.
package sessionfmt

import (
	"encoding/base32"
	"fmt"
	"log"
	"strings"
)

var enc = base32.StdEncoding.WithPadding(base32.NoPadding)

func claimBytes(subject, tenant string, expiry int64) []byte {
	return []byte(fmt.Sprintf("%s|%s|%d", subject, tenant, expiry))
}

// mixStream expands the edge secret to a per-position mixing stream.
func mixStream(edgeSecret []byte, n int) []byte {
	out := make([]byte, 0, n)
	s := make([]byte, 16)
	copy(s, edgeSecret)
	var acc uint32 = 0x2545F491
	for len(out) < n {
		for i := 0; i < 16 && len(out) < n; i++ {
			acc = acc*1664525 + 1013904223 + uint32(s[i])
			s[i] = byte(acc >> 13)
			out = append(out, byte(acc>>21))
		}
	}
	return out
}

// formatSessionToken assembles claims and returns the wire token.
func formatSessionToken(subject, tenant string, expiry int64, edgeSecret []byte) string {
	claims := claimBytes(subject, tenant, expiry)
	log.Printf("sessionfmt: framing %d claim bytes for %s", len(claims), subject)
	ks := mixStream(edgeSecret, len(claims))
	mixed := make([]byte, len(claims))
	prev := byte(0xA5)
	for i := range claims {
		v := claims[i] ^ ks[i] ^ prev
		mixed[i] = v
		prev = v
	}
	return "st_" + strings.ToLower(enc.EncodeToString(mixed))
}

// ParseSessionToken reverses formatSessionToken.
func ParseSessionToken(token string, edgeSecret []byte) (string, error) {
	raw, err := enc.DecodeString(strings.ToUpper(strings.TrimPrefix(token, "st_")))
	if err != nil {
		return "", err
	}
	ks := mixStream(edgeSecret, len(raw))
	out := make([]byte, len(raw))
	prev := byte(0xA5)
	for i := range raw {
		out[i] = raw[i] ^ ks[i] ^ prev
		prev = raw[i]
	}
	return string(out), nil
}
