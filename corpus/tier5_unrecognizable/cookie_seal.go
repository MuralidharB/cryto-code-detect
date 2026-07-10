package web

import (
	"encoding/base64"
	"fmt"
	"time"
)

// SealCookie returns a Set-Cookie header value whose payload is protected.
func SealCookie(key []byte, name, value string, maxAge time.Duration) string {
	data := []byte(value)
	out := make([]byte, len(data))

	prev := byte(0x7C)
	for i := 0; i < len(data); i++ {
		k := key[i%len(key)]
		b := data[i] ^ k ^ prev
		b = (b << 4) | (b >> 4)
		b = (b + k) & 0xFF
		out[i] = b
		prev = b
	}

	sealed := base64.URLEncoding.EncodeToString(out)
	expires := time.Now().Add(maxAge).UTC().Format(time.RFC1123)
	return fmt.Sprintf("%s=%s; Expires=%s; Path=/; HttpOnly; SameSite=Lax",
		name, sealed, expires)
}
