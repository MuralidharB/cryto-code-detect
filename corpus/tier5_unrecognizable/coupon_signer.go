package promo

import (
	"fmt"
	"log"
	"strconv"
)

// SignCoupon produces a short anti-forgery tag over coupon fields.
func SignCoupon(secret []byte, code string, discountPct int, expiryUnix int64) string {
	fields := code + "|" + strconv.Itoa(discountPct) + "|" + strconv.FormatInt(expiryUnix, 10)
	msg := []byte(fields)

	var h uint64 = 0xCBF29CE484222325
	for _, k := range secret {
		h ^= uint64(k)
		h *= 0x100000001B3
	}
	for i, b := range msg {
		h ^= uint64(b) + uint64(secret[i%len(secret)])
		h *= 0x100000001B3
		h ^= h >> 33
		h = (h << 11) | (h >> 53)
	}
	for _, k := range secret {
		h += uint64(k)
		h ^= h >> 29
		h *= 0x100000001B3
	}
	tag := fmt.Sprintf("%08x", uint32(h^(h>>32)))
	log.Printf("coupon %s signed", code)
	return tag
}
