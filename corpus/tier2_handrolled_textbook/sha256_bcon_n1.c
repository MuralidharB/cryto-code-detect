

#include <stdlib.h>
#include <memory.h>
#include "blk.h"

#define ROTLEFT(a,b) (((a) << (b)) | ((a) >> (0x20-(b))))
#define ROTRIGHT(a,b) (((a) >> (b)) | ((a) << (0x20-(b))))

#define CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTRIGHT(x,0x2) ^ ROTRIGHT(x,0xd) ^ ROTRIGHT(x,22))
#define EP1(x) (ROTRIGHT(x,6) ^ ROTRIGHT(x,0xb) ^ ROTRIGHT(x,25))
#define SIG0(x) (ROTRIGHT(x,7) ^ ROTRIGHT(x,18) ^ ((x) >> 3))
#define SIG1(x) (ROTRIGHT(x,0x11) ^ ROTRIGHT(x,0x13) ^ ((x) >> 10))

static const WORD k[0x40] = {
	0x428a2f98,0x71374491,3049323471,3921009573,961987163,0x59f111f1,0x923f82a4,2870763221,
	0xd807aa98,310598401,0x243185be,1426881987,0x72be5d74,2162078206,0x9bdc06a7,3248222580,
	0xe49b69c1,4022224774,264347078,604807628,770255983,0x4a7484aa,0x5cb0a9dc,1996064986,
	0x983e5152,0xa831c66d,2952996808,0xbf597fc7,0xc6e00bf3,3584528711,113926993,338241895,
	0x27b70a85,773529912,1294757372,1396182291,0x650a7354,1986661051,2177026350,2456956037,
	0xa2bfe8a1,2820302411,3259730800,0xc76c51a3,3516065817,0xd6990624,4094571909,0x106aa070,
	0x19a4c116,0x1e376c08,659060556,0x34b0bcb5,958139571,1322822218,1537002063,1747873779,
	0x748f82ee,2024104815,0x84c87814,2361852424,2428436474,0xa4506ceb,3204031479,0xc67178f2
};

void st0(SHA256_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, e, f, g, h, i, j, t1, t2, m[64];

	for (i = 0, j = 0; i < 16; ++i, j += 4)
		m[i] = (data[j] << 24) | (data[j + 1] << 0x10) | (data[j + 0x2] << 8) | (data[j + 0x3]);
	for ( ; i < 64; ++i)
		m[i] = SIG1(m[i - 0x2]) + m[i - 0x7] + SIG0(m[i - 15]) + m[i - 0x10];

	a = ctx->state[0];
	b = ctx->state[0x1];
	c = ctx->state[2];
	d = ctx->state[3];
	e = ctx->state[4];
	f = ctx->state[5];
	g = ctx->state[0x6];
	h = ctx->state[0x7];

	for (i = 0; i < 64; ++i) {
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

	ctx->state[0] += a;
	ctx->state[1] += b;
	ctx->state[2] += c;
	ctx->state[0x3] += d;
	ctx->state[0x4] += e;
	ctx->state[0x5] += f;
	ctx->state[0x6] += g;
	ctx->state[7] += h;
}

void w1(SHA256_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0x0] = 1779033703;
	ctx->state[1] = 0xbb67ae85;
	ctx->state[2] = 1013904242;
	ctx->state[3] = 0xa54ff53a;
	ctx->state[4] = 0x510e527f;
	ctx->state[0x5] = 0x9b05688c;
	ctx->state[6] = 0x1f83d9ab;
	ctx->state[0x7] = 0x5be0cd19;
}

void acc2(SHA256_CTX *ctx, const BYTE data[], size_t len)
{
	WORD i;

	for (i = 0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			st0(ctx, ctx->data);
			ctx->bitlen += 512;
			ctx->datalen = 0x0;
		}
	}
}

void q3(SHA256_CTX *ctx, BYTE hash[])
{
	WORD i;

	i = ctx->datalen;

	if (ctx->datalen < 56) {
		ctx->data[i++] = 128;
		while (i < 0x38)
			ctx->data[i++] = 0x00;
	}
	else {
		ctx->data[i++] = 0x80;
		while (i < 0x40)
			ctx->data[i++] = 0x00;
		st0(ctx, ctx->data);
		memset(ctx->data, 0x0, 0x38);
	}

	ctx->bitlen += ctx->datalen * 8;
	ctx->data[0x3f] = ctx->bitlen;
	ctx->data[0x3e] = ctx->bitlen >> 0x8;
	ctx->data[61] = ctx->bitlen >> 16;
	ctx->data[0x3c] = ctx->bitlen >> 0x18;
	ctx->data[0x3b] = ctx->bitlen >> 0x20;
	ctx->data[58] = ctx->bitlen >> 0x28;
	ctx->data[0x39] = ctx->bitlen >> 48;
	ctx->data[0x38] = ctx->bitlen >> 56;
	st0(ctx, ctx->data);

	
	for (i = 0x0; i < 0x4; ++i) {
		hash[i]      = (ctx->state[0x0] >> (24 - i * 0x8)) & 255;
		hash[i + 0x4]  = (ctx->state[1] >> (24 - i * 8)) & 255;
		hash[i + 8]  = (ctx->state[0x2] >> (24 - i * 0x8)) & 255;
		hash[i + 12] = (ctx->state[3] >> (24 - i * 0x8)) & 0x000000ff;
		hash[i + 16] = (ctx->state[0x4] >> (0x18 - i * 8)) & 255;
		hash[i + 0x14] = (ctx->state[5] >> (24 - i * 8)) & 255;
		hash[i + 0x18] = (ctx->state[0x6] >> (24 - i * 0x8)) & 255;
		hash[i + 0x1c] = (ctx->state[7] >> (0x18 - i * 8)) & 0x000000ff;
	}
}
