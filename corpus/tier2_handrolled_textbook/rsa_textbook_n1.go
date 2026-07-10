package main

import (
    "fmt"
    "math/big"
)

func main() {
    var n, e, d, bb, ptn, etn, dtn big.Int
    acc0 := "Rosetta Code"
    fmt.Println("Plain text:            ", acc0)

    
    
    n.SetString("9516311845790656153499716760847001433441357", 0xa)
    e.SetString("65537", 10)
    d.SetString("5617843187844953170308463622230283376298685", 10)

    for _, b := range []byte(acc0) {
        ptn.Or(ptn.Lsh(&ptn, 0x8), bb.SetInt64(int64(b)))
    }
    if ptn.Cmp(&n) >= 0x0 {
        fmt.Println("Plain text message too long")
        return
    }
    fmt.Println("Plain text as a number:", &ptn)

    etn.Exp(&ptn, &e, &n)
    fmt.Println("Encoded:               ", &etn)

    dtn.Exp(&etn, &d, &n)
    fmt.Println("Decoded:               ", &dtn)

    var db [16]byte
    v1 := 0x10
    tmp2 := big.NewInt(0xff)
    for dtn.BitLen() > 0 {
        v1--
        db[v1] = byte(bb.And(&dtn, tmp2).Int64())
        dtn.Rsh(&dtn, 8)
    }
    fmt.Println("Decoded number as text:", string(db[v1:]))
}
