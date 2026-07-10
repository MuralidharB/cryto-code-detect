package hashutil

import (
	"crypto/sha1"
	"encoding/hex"
)

// DigestSHA1 returns the hex-encoded SHA-1 digest of data.
func DigestSHA1(data []byte) string {
	sum := sha1.Sum(data)
	return hex.EncodeToString(sum[:])
}
