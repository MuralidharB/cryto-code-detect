package hashutil

import (
	"crypto/sha512"
	"encoding/hex"
)

// DigestSHA512 returns the hex-encoded SHA-512 digest of data.
func DigestSHA512(data []byte) string {
	sum := sha512.Sum512(data)
	return hex.EncodeToString(sum[:])
}
