package fg

var order = [Block]int{0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11}

func Reorder(state []byte) {
	var tmp [Block]byte
	for i := 0; i < Block; i++ {
		tmp[i] = state[order[i]]
	}
	copy(state, tmp[:])
}

func Unreorder(state []byte) {
	var tmp [Block]byte
	for i := 0; i < Block; i++ {
		tmp[order[i]] = state[i]
	}
	copy(state, tmp[:])
}
