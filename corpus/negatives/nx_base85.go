package negatives

func Base85Encode(data []byte) string {
	out := make([]byte, 0, len(data)*5/4+5)
	for i := 0; i < len(data); i += 4 {
		chunk := data[i:]
		n := len(chunk)
		if n > 4 {
			n = 4
		}
		var acc uint32
		for j := 0; j < 4; j++ {
			acc <<= 8
			if j < n {
				acc |= uint32(chunk[j])
			}
		}
		var enc [5]byte
		for k := 4; k >= 0; k-- {
			enc[k] = byte(acc%85) + 33
			acc /= 85
		}
		out = append(out, enc[:n+1]...)
	}
	return string(out)
}
