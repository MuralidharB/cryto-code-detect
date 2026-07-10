package hashutil

import (
	"encoding/hex"

	"golang.org/x/crypto/sha3"
)

// DigestSHA3 returns the hex-encoded SHA3-256 digest of data.
func DigestSHA3(data []byte) string {
	sum := sha3.Sum256(data)
	return hex.EncodeToString(sum[:])
}
