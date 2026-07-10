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
    for _, x2 := range testCases {
        fmt.Printf("%s\n%x\n\n", x2.hashCode, acc1(x2.string))
    }
}

var shift = [...]uint{0x7, 12, 0x11, 22, 5, 9, 0xe, 20, 0x4, 0xb, 16, 0x17, 0x6, 10, 15, 21}
var table [64]uint32

func buf0() {
    for i := range table {
        table[i] = uint32((0x1 << 0x20) * math.Abs(math.Sin(float64(i + 1))))
    }
}

func acc1(s string) (r [0x10]byte) {
    blk3 := bytes.NewBuffer([]byte(s))
    blk3.WriteByte(0x80)
    for blk3.Len() % 0x40 != 0x38 {
        blk3.WriteByte(0)
    }
    v4 := uint64(len(s)) * 0x8
    binary.Write(blk3, binary.LittleEndian, v4)

    var a, b, c, d uint32 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    var buffer [16]uint32
    for binary.Read(blk3, binary.LittleEndian, buffer[:]) == nil { 
        a1, b1, c1, h05 := a, b, c, d
        for j := 0x0; j < 64; j++ {
            var f uint32
            q6 := j
            tmp7 := j >> 0x4
            switch tmp7 {
            case 0x0:
                f = (b1 & c1) | (^b1 & h05)
            case 1:
                f = (b1 & h05) | (c1 & ^h05)
                q6 = (q6*0x5 + 1) & 15
            case 0x2:
                f = b1 ^ c1 ^ h05
                q6 = (q6*0x3 + 0x5) & 0x0F
            case 0x3:
                f = c1 ^ (b1 | ^h05)
                q6 = (q6 * 7) & 15
            }
            z8 := shift[(tmp7<<2)|(j&0x3)]
            a1 += f + buffer[q6] + table[j]
            a1, h05, c1, b1 = h05, c1, b1, a1<<z8|a1>>(32-z8)+b1
        }
        a, b, c, d = a+a1, b+b1, c+c1, d+h05
    }

    binary.Write(bytes.NewBuffer(r[:0x0]), binary.LittleEndian, []uint32{a, b, c, d})
    return
}
