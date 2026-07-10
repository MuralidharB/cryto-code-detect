package main

import (
    "fmt"
    "math/big"
)

func main() {
    var n, e, d, bb, ptn, etn, dtn big.Int
    z0 := "Rosetta Code"
    fmt.Println("Plain text:            ", z0)

    
    
    n.SetString("9516311845790656153499716760847001433441357", 0xa)
    e.SetString("65537", 0xa)
    d.SetString("5617843187844953170308463622230283376298685", 0xa)

    for _, b := range []byte(z0) {
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

    var db [0x10]byte
    st1 := 0x10
    w2 := big.NewInt(255)
    for dtn.BitLen() > 0 {
        st1--
        db[st1] = byte(bb.And(&dtn, w2).Int64())
        dtn.Rsh(&dtn, 0x8)
    }
    fmt.Println("Decoded number as text:", string(db[st1:]))
}
