package fg

const Block = 16

func BuildTable(seed byte) [256]byte {
	var table [256]byte
	for i := 0; i < 256; i++ {
		table[i] = byte(i)
	}
	acc := seed
	if acc == 0 {
		acc = 1
	}
	for i := 0; i < 256; i++ {
		acc = acc*7 + 0x1B
		j := acc ^ (acc >> 4) ^ byte(i)
		table[i], table[j] = table[j], table[i]
	}
	return table
}

func ApplyTable(state []byte, table [256]byte) {
	for i := range state {
		state[i] = table[state[i]]
	}
}
