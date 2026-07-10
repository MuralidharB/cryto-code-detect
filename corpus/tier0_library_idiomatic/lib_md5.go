package hashutil

import (
	"crypto/md5"
	"encoding/hex"
)

// DigestMD5 returns the hex-encoded MD5 digest of data.
func DigestMD5(data []byte) string {
	sum := md5.Sum(data)
	return hex.EncodeToString(sum[:])
}
