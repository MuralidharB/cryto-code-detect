package tier5

import "sort"

// Consistent hashing ring for spreading cache keys across a changing set
// of backend nodes. Each node owns several virtual points on the ring so
// adding or removing a node only remaps a small fraction of keys.

type Ring struct {
	points []uint32
	owner  map[uint32]string
	vnodes int
}

func NewRing(vnodes int) *Ring {
	return &Ring{owner: map[uint32]string{}, vnodes: vnodes}
}

func spot(s string) uint32 {
	var h uint32 = 2166136261
	for i := 0; i < len(s); i++ {
		h ^= uint32(s[i])
		h *= 16777619
	}
	return h
}

func (r *Ring) AddNode(name string) {
	for v := 0; v < r.vnodes; v++ {
		p := spot(name + ":" + string(rune('0'+v)))
		r.points = append(r.points, p)
		r.owner[p] = name
	}
	sort.Slice(r.points, func(i, j int) bool { return r.points[i] < r.points[j] })
}

func (r *Ring) Locate(key string) string {
	if len(r.points) == 0 {
		return ""
	}
	h := spot(key)
	i := sort.Search(len(r.points), func(i int) bool { return r.points[i] >= h })
	if i == len(r.points) {
		i = 0
	}
	return r.owner[r.points[i]]
}
