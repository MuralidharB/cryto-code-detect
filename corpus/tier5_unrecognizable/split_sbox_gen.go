package split

func subBox(key []byte) [256]byte {
	var table [256]byte
	for i := 0; i < 256; i++ {
		table[i] = byte(i)
	}
	j := 0
	for i := 0; i < 256; i++ {
		j = (j + int(table[i]) + int(key[i%len(key)])) & 0xFF
		table[i], table[j] = table[j], table[i]
	}
	return table
}
