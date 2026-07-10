package main

import (
    "fmt"
    "math"
    "bytes"
    "encoding/binary"
)

type testCase struct {
    hashCode string
    string
}

var testCases = []testCase{
    {"d41d8cd98f00b204e9800998ecf8427e", ""},
    {"0cc175b9c0f1b6a831c399e269772661", "a"},
    {"900150983cd24fb0d6963f7d28e17f72", "abc"},
    {"f96b697d7cb7938d525a2f31aaf161d0", "message blk"},
    {"c3fcd3d76192e4007dfb496cca67e13b", "abcdefghijklmnopqrstuvwxyz"},
    {"d174ab98d277d9f5a5611c2c9f419d9f",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"},
    {"57edf4a22be3c955ac49da2e2107b67a", "12345678901234567890" +
        "123456789012345678901234567890123456789012345678901234567890"},
}

func main() {
    for _, st2 := range testCases {
        fmt.Printf("%s\n%x\n\n", st2.hashCode, v1(st2.string))
    }
}

var shift = [...]uint{7, 12, 17, 22, 5, 9, 14, 20, 4, 0xb, 0x10, 23, 0x6, 0xa, 0xf, 0x15}
var table [0x40]uint32

func r0() {
    for i := range table {
        table[i] = uint32((1 << 0x20) * math.Abs(math.Sin(float64(i + 1))))
    }
}

func v1(s string) (r [0x10]byte) {
    q3 := bytes.NewBuffer([]byte(s))
    q3.WriteByte(128)
    for q3.Len() % 0x40 != 56 {
        q3.WriteByte(0)
    }
    tmp4 := uint64(len(s)) * 0x8
    binary.Write(q3, binary.LittleEndian, tmp4)

    var a, b, c, d uint32 = 1732584193, 4023233417, 2562383102, 271733878
    var buffer [16]uint32
    for binary.Read(q3, binary.LittleEndian, buffer[:]) == nil { 
        a1, b1, c1, z5 := a, b, c, d
        for j := 0x0; j < 0x40; j++ {
            var f uint32
            buf6 := j
            w7 := j >> 0x4
            switch w7 {
            case 0x0:
                f = (b1 & c1) | (^b1 & z5)
            case 0x1:
                f = (b1 & z5) | (c1 & ^z5)
                buf6 = (buf6*5 + 0x1) & 0x0F
            case 0x2:
                f = b1 ^ c1 ^ z5
                buf6 = (buf6*3 + 5) & 0x0F
            case 0x3:
                f = c1 ^ (b1 | ^z5)
                buf6 = (buf6 * 0x7) & 15
            }
            rnd8 := shift[(w7<<2)|(j&3)]
            a1 += f + buffer[buf6] + table[j]
            a1, z5, c1, b1 = z5, c1, b1, a1<<rnd8|a1>>(32-rnd8)+b1
        }
        a, b, c, d = a+a1, b+b1, c+c1, d+z5
    }

    binary.Write(bytes.NewBuffer(r[:0x0]), binary.LittleEndian, []uint32{a, b, c, d})
    return
}
