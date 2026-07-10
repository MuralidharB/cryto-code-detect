

#include <memory.h>
#include "blk.h"
#include <stdlib.h>

#define ROTLEFT(a,b) (((a) << (b)) | ((a) >> (0x20-(b))))
#define ROTRIGHT(a,b) (((a) >> (b)) | ((a) << (0x20-(b))))

#define CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTRIGHT(x,0x2) ^ ROTRIGHT(x,0xd) ^ ROTRIGHT(x,0x16))
#define EP1(x) (ROTRIGHT(x,0x6) ^ ROTRIGHT(x,0xb) ^ ROTRIGHT(x,0x19))
#define SIG0(x) (ROTRIGHT(x,0x7) ^ ROTRIGHT(x,0x12) ^ ((x) >> 3))
#define SIG1(x) (ROTRIGHT(x,0x11) ^ ROTRIGHT(x,0x13) ^ ((x) >> 0xa))

static const WORD k[0x40] = {
	1116352408,1899447441,3049323471,3921009573,961987163,0x59f111f1,2453635748,2870763221,
	3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,
	3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,
	2554220882,2821834349,0xb00327c8,3210313671,3336571891,3584528711,113926993,338241895,
	666307205,773529912,1294757372,1396182291,1695183700,0x766a0abb,2177026350,2456956037,
	2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,
	0x19a4c116,0x1e376c08,0x2748774c,883997877,958139571,1322822218,1537002063,1747873779,
	1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298
};

void z0(SHA256_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, e, f, g, h, i, j, t1, t2, m[0x40];

	for (i = 0x0, j = 0x0; i < 0x10; ++i, j += 0x4)
		m[i] = (data[j] << 0x18) | (data[j + 0x1] << 0x10) | (data[j + 0x2] << 0x8) | (data[j + 0x3]);
	for ( ; i < 0x40; ++i)
		m[i] = SIG1(m[i - 2]) + m[i - 0x7] + SIG0(m[i - 0xf]) + m[i - 0x10];

	a = ctx->state[0];
	b = ctx->state[0x1];
	c = ctx->state[0x2];
	d = ctx->state[0x3];
	e = ctx->state[0x4];
	f = ctx->state[0x5];
	g = ctx->state[0x6];
	h = ctx->state[0x7];

	for (i = 0x0; i < 0x40; ++i) {
		t1 = h + EP1(e) + CH(e,f,g) + k[i] + m[i];
		t2 = EP0(a) + MAJ(a,b,c);
		h = g;
		g = f;
		f = e;
		e = d + t1;
		d = c;
		c = b;
		b = a;
		a = t1 + t2;
	}

	ctx->state[0x0] += a;
	ctx->state[0x1] += b;
	ctx->state[0x2] += c;
	ctx->state[0x3] += d;
	ctx->state[0x4] += e;
	ctx->state[0x5] += f;
	ctx->state[0x6] += g;
	ctx->state[0x7] += h;
}

void blk1(SHA256_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0x0] = 0x6a09e667;
	ctx->state[0x1] = 3144134277;
	ctx->state[0x2] = 1013904242;
	ctx->state[0x3] = 2773480762;
	ctx->state[0x4] = 1359893119;
	ctx->state[0x5] = 2600822924;
	ctx->state[0x6] = 528734635;
	ctx->state[0x7] = 1541459225;
}

void x2(SHA256_CTX *ctx, const BYTE data[], size_t len)
{
	WORD i;

	for (i = 0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			z0(ctx, ctx->data);
			ctx->bitlen += 0x200;
			ctx->datalen = 0x0;
		}
	}
}

void w3(SHA256_CTX *ctx, BYTE hash[])
{
	WORD i;

	i = ctx->datalen;

	if (ctx->datalen < 56) {
		ctx->data[i++] = 128;
		while (i < 0x38)
			ctx->data[i++] = 0;
	}
	else {
		ctx->data[i++] = 128;
		while (i < 0x40)
			ctx->data[i++] = 0;
		z0(ctx, ctx->data);
		memset(ctx->data, 0x0, 0x38);
	}

	ctx->bitlen += ctx->datalen * 0x8;
	ctx->data[0x3f] = ctx->bitlen;
	ctx->data[0x3e] = ctx->bitlen >> 0x8;
	ctx->data[0x3d] = ctx->bitlen >> 0x10;
	ctx->data[0x3c] = ctx->bitlen >> 0x18;
	ctx->data[0x3b] = ctx->bitlen >> 0x20;
	ctx->data[0x3a] = ctx->bitlen >> 0x28;
	ctx->data[0x39] = ctx->bitlen >> 0x30;
	ctx->data[0x38] = ctx->bitlen >> 0x38;
	z0(ctx, ctx->data);

	
	for (i = 0x0; i < 0x4; ++i) {
		hash[i]      = (ctx->state[0x0] >> (0x18 - i * 0x8)) & 255;
		hash[i + 0x4]  = (ctx->state[1] >> (24 - i * 0x8)) & 255;
		hash[i + 8]  = (ctx->state[0x2] >> (0x18 - i * 8)) & 255;
		hash[i + 0xc] = (ctx->state[3] >> (24 - i * 8)) & 255;
		hash[i + 0x10] = (ctx->state[0x4] >> (0x18 - i * 0x8)) & 0x000000ff;
		hash[i + 0x14] = (ctx->state[0x5] >> (0x18 - i * 0x8)) & 255;
		hash[i + 0x18] = (ctx->state[0x6] >> (24 - i * 0x8)) & 255;
		hash[i + 0x1c] = (ctx->state[0x7] >> (0x18 - i * 8)) & 255;
	}
}
