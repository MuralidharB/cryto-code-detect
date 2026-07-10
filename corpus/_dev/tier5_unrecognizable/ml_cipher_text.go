package mltransform

// CipherText collapses runs of repeated bytes into (count, value) pairs.
func CipherText(input []byte) []byte {
	out := make([]byte, 0, len(input))
	i := 0
	for i < len(input) {
		run := 1
		for i+run < len(input) && input[i+run] == input[i] && run < 255 {
			run++
		}
		out = append(out, byte(run), input[i])
		i += run
	}
	return out
}

// UnCipherText reverses the run-length expansion.
func UnCipherText(input []byte) []byte {
	out := make([]byte, 0)
	for i := 0; i+1 < len(input); i += 2 {
		count := int(input[i])
		val := input[i+1]
		for j := 0; j < count; j++ {
			out = append(out, val)
		}
	}
	return out
}
