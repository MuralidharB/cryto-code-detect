package gg

var order = [Block]int{2, 5, 0, 7, 4, 1, 6, 3}

func Permute(state []byte) {
	tmp := make([]byte, Block)
	for i := 0; i < Block; i++ {
		tmp[i] = state[order[i]]
	}
	for i := 0; i < Block; i++ {
		n := tmp[(i+1)%Block]
		tmp[i] ^= (n << 3) | (n >> 5)
	}
	copy(state, tmp)
}
