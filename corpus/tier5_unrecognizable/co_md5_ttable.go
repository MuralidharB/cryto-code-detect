package main

import (
	"encoding/binary"
	"fmt"
	"math"
)

var tt [64]uint32
var shifts = [64]uint{
	7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
	5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
	4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
	6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
}

func initTable() {
	for i := 0; i < 64; i++ {
		v := math.Abs(math.Sin(float64(i + 1)))
		tt[i] = uint32(v * 4294967296.0)
	}
}

func rol(x uint32, c uint) uint32 {
	return (x << c) | (x >> (32 - c))
}

func compute(msg []byte) [16]byte {
	initTable()
	var a0, b0, c0, d0 uint32 = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476

	ml := uint64(len(msg)) * 8
	data := append([]byte{}, msg...)
	data = append(data, 0x80)
	for len(data)%64 != 56 {
		data = append(data, 0)
	}
	var lenBuf [8]byte
	binary.LittleEndian.PutUint64(lenBuf[:], ml)
	data = append(data, lenBuf[:]...)

	for off := 0; off < len(data); off += 64 {
		var m [16]uint32
		for i := 0; i < 16; i++ {
			m[i] = binary.LittleEndian.Uint32(data[off+i*4:])
		}
		a, b, c, d := a0, b0, c0, d0
		for i := 0; i < 64; i++ {
			var f uint32
			var g int
			switch {
			case i < 16:
				f = (b & c) | (^b & d)
				g = i
			case i < 32:
				f = (d & b) | (^d & c)
				g = (5*i + 1) % 16
			case i < 48:
				f = b ^ c ^ d
				g = (3*i + 5) % 16
			default:
				f = c ^ (b | ^d)
				g = (7 * i) % 16
			}
			f = f + a + tt[i] + m[g]
			a = d
			d = c
			c = b
			b = b + rol(f, shifts[i])
		}
		a0 += a
		b0 += b
		c0 += c
		d0 += d
	}

	var out [16]byte
	binary.LittleEndian.PutUint32(out[0:], a0)
	binary.LittleEndian.PutUint32(out[4:], b0)
	binary.LittleEndian.PutUint32(out[8:], c0)
	binary.LittleEndian.PutUint32(out[12:], d0)
	return out
}

func main() {
	out := compute([]byte("abc"))
	fmt.Printf("%x\n", out)
}
