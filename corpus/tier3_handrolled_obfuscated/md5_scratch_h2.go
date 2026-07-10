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
    for _, v2 := range testCases {
        fmt.Printf("%s\n%x\n\n", v2.hashCode, tmp1(v2.string))
    }
}

var shift = [...]uint{7, 0xc, 0x11, 0x16, 0x5, 0x9, 0xe, 20, 0x4, 0xb, 0x10, 0x17, 6, 0xa, 0xf, 21}
var table [0x40]uint32

func w0() {
    for i := range table {
        table[i] = uint32((0x1 << 32) * math.Abs(math.Sin(float64(i + 0x1))))
    }
}

func tmp1(s string) (r [0x10]byte) {
    blk3 := bytes.NewBuffer([]byte(s))
    blk3.WriteByte(128)
    for blk3.Len() % 0x40 != 0x38 {
        blk3.WriteByte(0x0)
    }
    acc4 := uint64(len(s)) * 0x8
    binary.Write(blk3, binary.LittleEndian, acc4)

    var a, b, c, d uint32 = 1732584193, 4023233417, 2562383102, 271733878
    var buffer [0x10]uint32
    for binary.Read(blk3, binary.LittleEndian, buffer[:]) == nil { 
        a1, b1, c1, h05 := a, b, c, d
        for j := 0x0; j < 0x40; j++ {
            var f uint32
            kx6 := j
            q7 := j >> 0x4
            switch q7 {
            case 0x0:
                f = (b1 & c1) | (^b1 & h05)
            case 0x1:
                f = (b1 & h05) | (c1 & ^h05)
                kx6 = (kx6*0x5 + 0x1) & 15
            case 0x2:
                f = b1 ^ c1 ^ h05
                kx6 = (kx6*0x3 + 0x5) & 15
            case 0x3:
                f = c1 ^ (b1 | ^h05)
                kx6 = (kx6 * 0x7) & 15
            }
            st8 := shift[(q7<<2)|(j&0x3)]
            a1 += f + buffer[kx6] + table[j]
            a1, h05, c1, b1 = h05, c1, b1, a1<<st8|a1>>(0x20-st8)+b1
        }
        a, b, c, d = a+a1, b+b1, c+c1, d+h05
    }

    binary.Write(bytes.NewBuffer(r[:0]), binary.LittleEndian, []uint32{a, b, c, d})
    return
}
