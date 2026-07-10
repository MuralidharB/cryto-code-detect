package fg

const Rounds = 6

func Expand(master []byte) [][]byte {
	data := make([]byte, len(master))
	copy(data, master)
	if len(data) == 0 {
		data = []byte{1}
	}
	var words []byte
	for len(words) < Block*(Rounds+1) {
		for i := range data {
			data[i] = data[i] + data[(i+1)%len(data)] + byte(len(words)+1)
			data[i] = (data[i] << 1) | (data[i] >> 7)
		}
		words = append(words, data...)
	}
	out := make([][]byte, Rounds+1)
	for r := 0; r <= Rounds; r++ {
		out[r] = words[r*Block : (r+1)*Block]
	}
	return out
}
