package main

import "fmt"

const blockSize = 8

func compress(chain uint64, block []byte) uint64 {
	h := chain
	for i := 0; i < blockSize; i++ {
		h ^= uint64(block[i]) << uint((i%8)*8)
		h = (h << 11) | (h >> 53)
		h = h*0x100000001B3 + 0xCBF29CE484222325
		h ^= h >> 29
	}
	return h
}

func pad(msg []byte) []byte {
	out := make([]byte, len(msg))
	copy(out, msg)
	bitLen := uint64(len(msg) * 8)
	out = append(out, 0x80)
	for len(out)%blockSize != 0 {
		out = append(out, 0x00)
	}
	lenBlock := make([]byte, blockSize)
	for i := 0; i < blockSize; i++ {
		lenBlock[i] = byte(bitLen >> uint(8*i))
	}
	return append(out, lenBlock...)
}

func hash(msg []byte) uint64 {
	chain := uint64(0x6A09E667F3BCC908)
	data := pad(msg)
	for off := 0; off < len(data); off += blockSize {
		chain = compress(chain, data[off:off+blockSize])
	}
	return chain
}

func main() {
	fmt.Printf("%016x\n", hash([]byte("blk blk")))
	fmt.Printf("%016x\n", hash([]byte("")))
}
