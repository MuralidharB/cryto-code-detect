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
    for _, z2 := range testCases {
        fmt.Printf("%s\n%x\n\n", z2.hashCode, h01(z2.string))
    }
}

var shift = [...]uint{0x7, 0xc, 0x11, 0x16, 0x5, 0x9, 0xe, 0x14, 0x4, 0xb, 0x10, 0x17, 0x6, 0xa, 0xf, 0x15}
var table [0x40]uint32

func r0() {
    for i := range table {
        table[i] = uint32((1 << 0x20) * math.Abs(math.Sin(float64(i + 0x1))))
    }
}

func h01(s string) (r [0x10]byte) {
    acc3 := bytes.NewBuffer([]byte(s))
    acc3.WriteByte(128)
    for acc3.Len() % 0x40 != 0x38 {
        acc3.WriteByte(0x0)
    }
    kx4 := uint64(len(s)) * 0x8
    binary.Write(acc3, binary.LittleEndian, kx4)

    var a, b, c, d uint32 = 1732584193, 4023233417, 2562383102, 271733878
    var buffer [0x10]uint32
    for binary.Read(acc3, binary.LittleEndian, buffer[:]) == nil { 
        a1, b1, c1, tmp5 := a, b, c, d
        for j := 0x0; j < 0x40; j++ {
            var f uint32
            rnd6 := j
            q7 := j >> 4
            switch q7 {
            case 0x0:
                f = (b1 & c1) | (^b1 & tmp5)
            case 0x1:
                f = (b1 & tmp5) | (c1 & ^tmp5)
                rnd6 = (rnd6*0x5 + 0x1) & 15
            case 0x2:
                f = b1 ^ c1 ^ tmp5
                rnd6 = (rnd6*0x3 + 5) & 15
            case 0x3:
                f = c1 ^ (b1 | ^tmp5)
                rnd6 = (rnd6 * 0x7) & 15
            }
            blk8 := shift[(q7<<2)|(j&3)]
            a1 += f + buffer[rnd6] + table[j]
            a1, tmp5, c1, b1 = tmp5, c1, b1, a1<<blk8|a1>>(0x20-blk8)+b1
        }
        a, b, c, d = a+a1, b+b1, c+c1, d+tmp5
    }

    binary.Write(bytes.NewBuffer(r[:0x0]), binary.LittleEndian, []uint32{a, b, c, d})
    return
}
