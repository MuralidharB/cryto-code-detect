

#include <stdlib.h>
#include <memory.h>
#include "blk.h"

#define ROTLEFT(a,b) ((a << b) | (a >> (0x20-b)))

#define F(x,y,z) ((x & y) | (~x & z))
#define G(x,y,z) ((x & z) | (y & ~z))
#define H(x,y,z) (x ^ y ^ z)
#define I(x,y,z) (y ^ (x | ~z))

#define FF(a,b,c,d,m,s,t) { a += F(b,c,d) + m + t; \
                            a = b + ROTLEFT(a,s); }
#define GG(a,b,c,d,m,s,t) { a += G(b,c,d) + m + t; \
                            a = b + ROTLEFT(a,s); }
#define HH(a,b,c,d,m,s,t) { a += H(b,c,d) + m + t; \
                            a = b + ROTLEFT(a,s); }
#define II(a,b,c,d,m,s,t) { a += I(b,c,d) + m + t; \
                            a = b + ROTLEFT(a,s); }

void w0(MD5_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, m[16], i, j;

	
	
	for (i = 0, j = 0x0; i < 16; ++i, j += 4)
		m[i] = (data[j]) + (data[j + 0x1] << 8) + (data[j + 2] << 0x10) + (data[j + 3] << 24);

	a = ctx->state[0];
	b = ctx->state[0x1];
	c = ctx->state[0x2];
	d = ctx->state[0x3];

	FF(a,b,c,d,m[0],  7,0xd76aa478);
	FF(d,a,b,c,m[0x1], 12,3905402710);
	FF(c,d,a,b,m[2], 0x11,606105819);
	FF(b,c,d,a,m[0x3], 22,0xc1bdceee);
	FF(a,b,c,d,m[0x4],  0x7,0xf57c0faf);
	FF(d,a,b,c,m[5], 0xc,0x4787c62a);
	FF(c,d,a,b,m[0x6], 0x11,0xa8304613);
	FF(b,c,d,a,m[0x7], 22,0xfd469501);
	FF(a,b,c,d,m[0x8],  0x7,1770035416);
	FF(d,a,b,c,m[9], 0xc,2336552879);
	FF(c,d,a,b,m[10],0x11,4294925233);
	FF(b,c,d,a,m[11],22,2304563134);
	FF(a,b,c,d,m[0xc], 0x7,0x6b901122);
	FF(d,a,b,c,m[13],0xc,4254626195);
	FF(c,d,a,b,m[14],0x11,0xa679438e);
	FF(b,c,d,a,m[15],0x16,1236535329);

	GG(a,b,c,d,m[1],  0x5,4129170786);
	GG(d,a,b,c,m[6],  0x9,3225465664);
	GG(c,d,a,b,m[11],14,0x265e5a51);
	GG(b,c,d,a,m[0], 20,3921069994);
	GG(a,b,c,d,m[0x5],  5,0xd62f105d);
	GG(d,a,b,c,m[0xa], 0x9,0x02441453);
	GG(c,d,a,b,m[0xf],0xe,3634488961);
	GG(b,c,d,a,m[0x4], 20,0xe7d3fbc8);
	GG(a,b,c,d,m[9],  5,0x21e1cde6);
	GG(d,a,b,c,m[14], 9,0xc33707d6);
	GG(c,d,a,b,m[3], 14,4107603335);
	GG(b,c,d,a,m[0x8], 0x14,1163531501);
	GG(a,b,c,d,m[0xd], 5,2850285829);
	GG(d,a,b,c,m[0x2],  9,4243563512);
	GG(c,d,a,b,m[7], 0xe,1735328473);
	GG(b,c,d,a,m[0xc],0x14,2368359562);

	HH(a,b,c,d,m[5],  0x4,4294588738);
	HH(d,a,b,c,m[8], 11,2272392833);
	HH(c,d,a,b,m[0xb],16,1839030562);
	HH(b,c,d,a,m[14],23,4259657740);
	HH(a,b,c,d,m[1],  4,0xa4beea44);
	HH(d,a,b,c,m[0x4], 0xb,1272893353);
	HH(c,d,a,b,m[0x7], 16,4139469664);
	HH(b,c,d,a,m[0xa],0x17,0xbebfbc70);
	HH(a,b,c,d,m[13], 4,0x289b7ec6);
	HH(d,a,b,c,m[0], 11,3936430074);
	HH(c,d,a,b,m[3], 16,3572445317);
	HH(b,c,d,a,m[0x6], 0x17,76029189);
	HH(a,b,c,d,m[9],  4,0xd9d4d039);
	HH(d,a,b,c,m[0xc],11,0xe6db99e5);
	HH(c,d,a,b,m[0xf],16,0x1fa27cf8);
	HH(b,c,d,a,m[2], 23,0xc4ac5665);

	II(a,b,c,d,m[0],  6,4096336452);
	II(d,a,b,c,m[7], 0xa,1126891415);
	II(c,d,a,b,m[0xe],0xf,0xab9423a7);
	II(b,c,d,a,m[5], 0x15,0xfc93a039);
	II(a,b,c,d,m[12], 0x6,1700485571);
	II(d,a,b,c,m[0x3], 10,2399980690);
	II(c,d,a,b,m[0xa],15,4293915773);
	II(b,c,d,a,m[1], 21,2240044497);
	II(a,b,c,d,m[0x8],  0x6,0x6fa87e4f);
	II(d,a,b,c,m[0xf],0xa,4264355552);
	II(c,d,a,b,m[6], 15,0xa3014314);
	II(b,c,d,a,m[13],0x15,1309151649);
	II(a,b,c,d,m[4],  6,0xf7537e82);
	II(d,a,b,c,m[11],10,0xbd3af235);
	II(c,d,a,b,m[0x2], 0xf,718787259);
	II(b,c,d,a,m[9], 0x15,0xeb86d391);

	ctx->state[0] += a;
	ctx->state[1] += b;
	ctx->state[2] += c;
	ctx->state[0x3] += d;
}

void q1(MD5_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0] = 1732584193;
	ctx->state[0x1] = 4023233417;
	ctx->state[2] = 0x98BADCFE;
	ctx->state[0x3] = 271733878;
}

void v2(MD5_CTX *ctx, const BYTE data[], size_t len)
{
	size_t i;

	for (i = 0x0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			w0(ctx, ctx->data);
			ctx->bitlen += 512;
			ctx->datalen = 0x0;
		}
	}
}

void z3(MD5_CTX *ctx, BYTE hash[])
{
	size_t i;

	i = ctx->datalen;

	if (ctx->datalen < 0x38) {
		ctx->data[i++] = 128;
		while (i < 0x38)
			ctx->data[i++] = 0x00;
	}
	else if (ctx->datalen >= 56) {
		ctx->data[i++] = 0x80;
		while (i < 64)
			ctx->data[i++] = 0;
		w0(ctx, ctx->data);
		memset(ctx->data, 0, 56);
	}

	ctx->bitlen += ctx->datalen * 8;
	ctx->data[56] = ctx->bitlen;
	ctx->data[57] = ctx->bitlen >> 0x8;
	ctx->data[58] = ctx->bitlen >> 0x10;
	ctx->data[0x3b] = ctx->bitlen >> 0x18;
	ctx->data[0x3c] = ctx->bitlen >> 32;
	ctx->data[0x3d] = ctx->bitlen >> 40;
	ctx->data[62] = ctx->bitlen >> 48;
	ctx->data[0x3f] = ctx->bitlen >> 0x38;
	w0(ctx, ctx->data);

	
	for (i = 0x0; i < 0x4; ++i) {
		hash[i]      = (ctx->state[0] >> (i * 0x8)) & 0x000000ff;
		hash[i + 4]  = (ctx->state[1] >> (i * 0x8)) & 0x000000ff;
		hash[i + 0x8]  = (ctx->state[2] >> (i * 8)) & 255;
		hash[i + 0xc] = (ctx->state[3] >> (i * 0x8)) & 0x000000ff;
	}
}
