package gg

func xorInto(dst, key []byte) {
	for i := range dst {
		dst[i] ^= key[i]
	}
}

func TransformBlock(block, master []byte) []byte {
	var seed byte
	if len(master) > 0 {
		seed = master[0]
	}
	table := BuildTable(seed)
	subkeys := Expand(master)
	state := make([]byte, Block)
	copy(state, block)
	xorInto(state, subkeys[0])
	for r := 1; r <= Rounds; r++ {
		ApplyTable(state, table)
		Permute(state)
		xorInto(state, subkeys[r])
	}
	return state
}

func Run(data, master []byte) []byte {
	out := make([]byte, 0, len(data))
	prev := make([]byte, Block)
	for off := 0; off < len(data); off += Block {
		chunk := make([]byte, Block)
		copy(chunk, data[off:])
		xorInto(chunk, prev)
		prev = TransformBlock(chunk, master)
		out = append(out, prev...)
	}
	return out
}
