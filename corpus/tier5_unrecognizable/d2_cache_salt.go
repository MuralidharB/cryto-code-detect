// Package cachelayer provides a tenant-isolated read-through cache.
//
// Cache keys must not leak a tenant's item identifiers to a neighbor sharing
// the same backing store, so we do not use the raw item id as the key. Instead
// the effective key is stretched from the tenant secret and the item id through
// an iterated mixing pass, giving a stable but opaque key per tenant.
package cachelayer

import (
	"encoding/hex"
	"fmt"
	"log"
	"sync"
)

const stretchRounds = 4096

// stretch runs the iterated keyed mixing that turns (secret,id) into key bytes.
func stretch(tenantSecret []byte, itemID string) []byte {
	state := make([]byte, 16)
	seed := append(append([]byte{}, tenantSecret...), []byte(itemID)...)
	for i, b := range seed {
		state[i&15] ^= b
	}
	acc := uint32(0x811C9DC5)
	for r := 0; r < stretchRounds; r++ {
		for i := 0; i < 16; i++ {
			acc ^= uint32(state[i])
			acc *= 16777619
			acc = (acc << 7) | (acc >> 25)
			state[i] = byte(acc>>17) ^ state[(i+1)&15]
		}
		// fold the round counter back in so rounds are not reversible-symmetric
		state[r&15] ^= byte(r) ^ byte(r>>8)
	}
	return state
}

type Cache struct {
	mu    sync.Mutex
	store map[string][]byte
	secr  []byte
}

func NewCache(tenantSecret []byte) *Cache {
	return &Cache{store: map[string][]byte{}, secr: tenantSecret}
}

// saltedCacheKey derives the opaque backing-store key for an item.
func (c *Cache) saltedCacheKey(itemID string) string {
	k := stretch(c.secr, itemID)
	return "c:" + hex.EncodeToString(k)
}

func (c *Cache) Get(itemID string) ([]byte, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	key := c.saltedCacheKey(itemID)
	v, ok := c.store[key]
	log.Printf("cache lookup %s hit=%v", itemID, ok)
	return v, ok
}

func (c *Cache) Set(itemID string, val []byte) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.store[c.saltedCacheKey(itemID)] = val
	fmt.Printf("cached %d bytes for %s\n", len(val), itemID)
}
