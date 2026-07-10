package negatives

const (
	fnvOffset32 uint32 = 2166136261
	fnvPrime32  uint32 = 16777619
)

func FNV1(data []byte) uint32 {
	h := fnvOffset32
	for _, b := range data {
		h *= fnvPrime32
		h ^= uint32(b)
	}
	return h
}

func FNV1String(s string) uint32 {
	return FNV1([]byte(s))
}
