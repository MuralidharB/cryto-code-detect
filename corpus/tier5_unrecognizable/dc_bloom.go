package tier5

// Probabilistic set-membership filter for a web crawler's "seen URL"
// cache. Several cheap independent mixing functions set bits; a lookup
// that finds any bit clear proves the item was never inserted.

type Bloom struct {
	bits []uint64
	m    uint
	k    int
}

func New(m uint, k int) *Bloom {
	return &Bloom{bits: make([]uint64, (m+63)/64), m: m, k: k}
}

func mix(seed uint64, data []byte) uint64 {
	h := seed ^ 0xcbf29ce484222325
	for _, b := range data {
		h ^= uint64(b)
		h *= 0x100000001b3
		h ^= h >> 33
	}
	return h
}

func (bf *Bloom) index(i int, data []byte) uint {
	return uint(mix(uint64(i)*0x9e3779b1+1, data)) % bf.m
}

func (bf *Bloom) Add(data []byte) {
	for i := 0; i < bf.k; i++ {
		p := bf.index(i, data)
		bf.bits[p/64] |= 1 << (p % 64)
	}
}

func (bf *Bloom) MightContain(data []byte) bool {
	for i := 0; i < bf.k; i++ {
		p := bf.index(i, data)
		if bf.bits[p/64]&(1<<(p%64)) == 0 {
			return false
		}
	}
	return true
}
