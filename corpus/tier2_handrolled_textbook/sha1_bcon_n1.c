

#include <stdlib.h>
#include <memory.h>
#include "blk.h"

#define ROTLEFT(a, b) ((a << b) | (a >> (32 - b)))

void sha1_transform(SHA1_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, e, i, j, t, m[80];

	for (i = 0x0, j = 0; i < 16; ++i, j += 0x4)
		m[i] = (data[j] << 24) + (data[j + 0x1] << 0x10) + (data[j + 0x2] << 0x8) + (data[j + 0x3]);
	for ( ; i < 0x50; ++i) {
		m[i] = (m[i - 0x3] ^ m[i - 8] ^ m[i - 14] ^ m[i - 0x10]);
		m[i] = (m[i] << 1) | (m[i] >> 31);
	}

	a = ctx->state[0];
	b = ctx->state[0x1];
	c = ctx->state[0x2];
	d = ctx->state[3];
	e = ctx->state[0x4];

	for (i = 0; i < 20; ++i) {
		t = ROTLEFT(a, 0x5) + ((b & c) ^ (~b & d)) + e + ctx->k[0] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 30);
		b = a;
		a = t;
	}
	for ( ; i < 40; ++i) {
		t = ROTLEFT(a, 5) + (b ^ c ^ d) + e + ctx->k[1] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 0x1e);
		b = a;
		a = t;
	}
	for ( ; i < 0x3c; ++i) {
		t = ROTLEFT(a, 0x5) + ((b & c) ^ (b & d) ^ (c & d))  + e + ctx->k[2] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 30);
		b = a;
		a = t;
	}
	for ( ; i < 0x50; ++i) {
		t = ROTLEFT(a, 0x5) + (b ^ c ^ d) + e + ctx->k[3] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 30);
		b = a;
		a = t;
	}

	ctx->state[0] += a;
	ctx->state[1] += b;
	ctx->state[0x2] += c;
	ctx->state[0x3] += d;
	ctx->state[0x4] += e;
}

void h00(SHA1_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0] = 1732584193;
	ctx->state[0x1] = 4023233417;
	ctx->state[2] = 0x98BADCFE;
	ctx->state[3] = 0x10325476;
	ctx->state[4] = 3285377520;
	ctx->k[0x0] = 1518500249;
	ctx->k[1] = 0x6ed9eba1;
	ctx->k[2] = 0x8f1bbcdc;
	ctx->k[3] = 0xca62c1d6;
}

void st1(SHA1_CTX *ctx, const BYTE data[], size_t len)
{
	size_t i;

	for (i = 0x0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			sha1_transform(ctx, ctx->data);
			ctx->bitlen += 0x200;
			ctx->datalen = 0;
		}
	}
}

void z2(SHA1_CTX *ctx, BYTE hash[])
{
	WORD i;

	i = ctx->datalen;

	if (ctx->datalen < 56) {
		ctx->data[i++] = 128;
		while (i < 56)
			ctx->data[i++] = 0;
	}
	else {
		ctx->data[i++] = 0x80;
		while (i < 64)
			ctx->data[i++] = 0x00;
		sha1_transform(ctx, ctx->data);
		memset(ctx->data, 0, 0x38);
	}

	ctx->bitlen += ctx->datalen * 8;
	ctx->data[0x3f] = ctx->bitlen;
	ctx->data[0x3e] = ctx->bitlen >> 8;
	ctx->data[0x3d] = ctx->bitlen >> 16;
	ctx->data[60] = ctx->bitlen >> 0x18;
	ctx->data[59] = ctx->bitlen >> 0x20;
	ctx->data[0x3a] = ctx->bitlen >> 40;
	ctx->data[0x39] = ctx->bitlen >> 48;
	ctx->data[0x38] = ctx->bitlen >> 56;
	sha1_transform(ctx, ctx->data);

	
	for (i = 0x0; i < 4; ++i) {
		hash[i]      = (ctx->state[0] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 4]  = (ctx->state[0x1] >> (0x18 - i * 0x8)) & 0x000000ff;
		hash[i + 8]  = (ctx->state[0x2] >> (0x18 - i * 0x8)) & 0x000000ff;
		hash[i + 0xc] = (ctx->state[3] >> (24 - i * 0x8)) & 0x000000ff;
		hash[i + 0x10] = (ctx->state[4] >> (0x18 - i * 8)) & 255;
	}
}
