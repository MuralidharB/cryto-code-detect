package gg

const Rounds = 4

func Expand(master []byte) [][]byte {
	words := make([]byte, Block)
	for i := 0; i < Block; i++ {
		if i < len(master) {
			words[i] = master[i]
		} else {
			words[i] = byte(i)
		}
	}
	subkeys := make([][]byte, 0, Rounds+1)
	rc := byte(1)
	for r := 0; r <= Rounds; r++ {
		for i := 0; i < Block; i++ {
			words[i] = words[i] + words[(i+1)%Block] + rc
			words[i] = (words[i] << 1) | (words[i] >> 7)
		}
		sk := make([]byte, Block)
		copy(sk, words)
		subkeys = append(subkeys, sk)
		rc = rc*3 + 1
	}
	return subkeys
}
