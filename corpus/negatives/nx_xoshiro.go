package negatives

type Xoshiro256 struct {
	s [4]uint64
}

func rotl(x uint64, k uint) uint64 {
	return (x << k) | (x >> (64 - k))
}

func (x *Xoshiro256) Next() uint64 {
	result := rotl(x.s[1]*5, 7) * 9
	t := x.s[1] << 17
	x.s[2] ^= x.s[0]
	x.s[3] ^= x.s[1]
	x.s[1] ^= x.s[2]
	x.s[0] ^= x.s[3]
	x.s[2] ^= t
	x.s[3] = rotl(x.s[3], 45)
	return result
}

func NewXoshiro256(seed uint64) *Xoshiro256 {
	x := &Xoshiro256{}
	for i := range x.s {
		seed += 0x9E3779B97F4A7C15
		x.s[i] = seed
	}
	return x
}
