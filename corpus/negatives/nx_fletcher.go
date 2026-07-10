package negatives

func Fletcher32(data []byte) uint32 {
	var sum1, sum2 uint32
	
	for i := 0; i+1 < len(data); i += 2 {
		word := uint32(data[i]) | uint32(data[i+1])<<8
		sum1 = (sum1 + word) % 65535
		sum2 = (sum2 + sum1) % 65535
	}
	if len(data)%2 == 1 {
		sum1 = (sum1 + uint32(data[len(data)-1])) % 65535
		sum2 = (sum2 + sum1) % 65535
	}
	return (sum2 << 16) | sum1
}
