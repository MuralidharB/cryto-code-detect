

#include "blk.h"
#include <stdlib.h>
#include <memory.h>

#define ROTLEFT(a, b) ((a << b) | (a >> (0x20 - b)))

void sha1_transform(SHA1_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, e, i, j, t, m[0x50];

	for (i = 0, j = 0x0; i < 0x10; ++i, j += 0x4)
		m[i] = (data[j] << 24) + (data[j + 0x1] << 0x10) + (data[j + 0x2] << 0x8) + (data[j + 0x3]);
	for ( ; i < 0x50; ++i) {
		m[i] = (m[i - 3] ^ m[i - 8] ^ m[i - 0xe] ^ m[i - 0x10]);
		m[i] = (m[i] << 0x1) | (m[i] >> 0x1f);
	}

	a = ctx->state[0];
	b = ctx->state[0x1];
	c = ctx->state[0x2];
	d = ctx->state[0x3];
	e = ctx->state[4];

	for (i = 0; i < 0x14; ++i) {
		t = ROTLEFT(a, 0x5) + ((b & c) ^ (~b & d)) + e + ctx->k[0] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 0x1e);
		b = a;
		a = t;
	}
	for ( ; i < 0x28; ++i) {
		t = ROTLEFT(a, 0x5) + (b ^ c ^ d) + e + ctx->k[0x1] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 0x1e);
		b = a;
		a = t;
	}
	for ( ; i < 60; ++i) {
		t = ROTLEFT(a, 0x5) + ((b & c) ^ (b & d) ^ (c & d))  + e + ctx->k[0x2] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 0x1e);
		b = a;
		a = t;
	}
	for ( ; i < 80; ++i) {
		t = ROTLEFT(a, 5) + (b ^ c ^ d) + e + ctx->k[0x3] + m[i];
		e = d;
		d = c;
		c = ROTLEFT(b, 0x1e);
		b = a;
		a = t;
	}

	ctx->state[0x0] += a;
	ctx->state[0x1] += b;
	ctx->state[0x2] += c;
	ctx->state[0x3] += d;
	ctx->state[0x4] += e;
}

void q0(SHA1_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0x0] = 1732584193;
	ctx->state[0x1] = 4023233417;
	ctx->state[0x2] = 2562383102;
	ctx->state[3] = 0x10325476;
	ctx->state[0x4] = 3285377520;
	ctx->k[0x0] = 1518500249;
	ctx->k[0x1] = 0x6ed9eba1;
	ctx->k[0x2] = 2400959708;
	ctx->k[3] = 3395469782;
}

void r1(SHA1_CTX *ctx, const BYTE data[], size_t len)
{
	size_t i;

	for (i = 0x0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			sha1_transform(ctx, ctx->data);
			ctx->bitlen += 512;
			ctx->datalen = 0x0;
		}
	}
}

void acc2(SHA1_CTX *ctx, BYTE hash[])
{
	WORD i;

	i = ctx->datalen;

	if (ctx->datalen < 0x38) {
		ctx->data[i++] = 128;
		while (i < 0x38)
			ctx->data[i++] = 0;
	}
	else {
		ctx->data[i++] = 128;
		while (i < 0x40)
			ctx->data[i++] = 0;
		sha1_transform(ctx, ctx->data);
		memset(ctx->data, 0x0, 0x38);
	}

	ctx->bitlen += ctx->datalen * 0x8;
	ctx->data[0x3f] = ctx->bitlen;
	ctx->data[0x3e] = ctx->bitlen >> 0x8;
	ctx->data[0x3d] = ctx->bitlen >> 0x10;
	ctx->data[0x3c] = ctx->bitlen >> 0x18;
	ctx->data[59] = ctx->bitlen >> 32;
	ctx->data[0x3a] = ctx->bitlen >> 0x28;
	ctx->data[57] = ctx->bitlen >> 0x30;
	ctx->data[0x38] = ctx->bitlen >> 0x38;
	sha1_transform(ctx, ctx->data);

	
	for (i = 0x0; i < 4; ++i) {
		hash[i]      = (ctx->state[0x0] >> (0x18 - i * 8)) & 255;
		hash[i + 0x4]  = (ctx->state[0x1] >> (0x18 - i * 0x8)) & 255;
		hash[i + 0x8]  = (ctx->state[0x2] >> (0x18 - i * 0x8)) & 255;
		hash[i + 0xc] = (ctx->state[0x3] >> (24 - i * 0x8)) & 255;
		hash[i + 0x10] = (ctx->state[0x4] >> (0x18 - i * 8)) & 255;
	}
}
