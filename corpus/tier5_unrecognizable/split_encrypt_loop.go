package split

const rounds = 12

func transformBlock(block, key []byte) []byte {
	table := subBox(key)
	state := make([]byte, blockLen)
	for i := 0; i < blockLen; i++ {
		state[i] = block[i] ^ key[i%len(key)]
	}
	for r := 0; r < rounds; r++ {
		for i := 0; i < blockLen; i++ {
			state[i] = table[state[i]]
		}
		state = shuffle(state)
		for i := 0; i < blockLen; i++ {
			state[i] ^= key[(i+r)%len(key)]
		}
	}
	return state
}
