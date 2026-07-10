package main

import "fmt"

const (
	prime = 263
	aCoef = 2
)

type point struct {
	x, y int
	inf  bool
}

func mod(v int) int {
	v %= prime
	if v < 0 {
		v += prime
	}
	return v
}

func inv(v int) int {
	r := 1
	e := prime - 2
	b := mod(v)
	for e > 0 {
		if e&1 == 1 {
			r = mod(r * b)
		}
		b = mod(b * b)
		e >>= 1
	}
	return r
}

func add(p, q point) point {
	if p.inf {
		return q
	}
	if q.inf {
		return p
	}
	if p.x == q.x && mod(p.y+q.y) == 0 {
		return point{inf: true}
	}
	var lam int
	if p.x == q.x && p.y == q.y {
		lam = mod((3*p.x*p.x + aCoef) * inv(2*p.y))
	} else {
		lam = mod((q.y - p.y) * inv(mod(q.x-p.x)))
	}
	rx := mod(lam*lam - p.x - q.x)
	ry := mod(lam*(p.x-rx) - p.y)
	return point{x: rx, y: ry}
}

func scalarMul(k int, g point) point {
	r := point{inf: true}
	add0 := g
	for k > 0 {
		if k&1 == 1 {
			r = add(r, add0)
		}
		add0 = add(add0, add0)
		k >>= 1
	}
	return r
}

func main() {
	g := point{x: 11, y: 87}
	pub := scalarMul(42, g)
	fmt.Printf("Q = (%d, %d) inf=%v\n", pub.x, pub.y, pub.inf)
}
