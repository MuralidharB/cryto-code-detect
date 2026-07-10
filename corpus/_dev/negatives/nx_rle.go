package negatives

func RLEEncode(data []byte) []byte {
	out := make([]byte, 0, len(data))
	for i := 0; i < len(data); {
		b := data[i]
		count := 1
		for i+count < len(data) && data[i+count] == b && count < 255 {
			count++
		}
		out = append(out, byte(count), b)
		i += count
	}
	return out
}

func RLEDecode(data []byte) []byte {
	out := make([]byte, 0, len(data))
	for i := 0; i+1 < len(data); i += 2 {
		count, b := data[i], data[i+1]
		for j := byte(0); j < count; j++ {
			out = append(out, b)
		}
	}
	return out
}
