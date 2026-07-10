package hashutil

import (
	"crypto/sha256"
	"encoding/hex"
)

// DigestSHA256 returns the hex-encoded SHA-256 digest of data.
func DigestSHA256(data []byte) string {
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:])
}
