

#include <memory.h>
#include <stdlib.h>
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

void z0(MD5_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, m[0x10], i, j;

	
	
	for (i = 0x0, j = 0x0; i < 0x10; ++i, j += 0x4)
		m[i] = (data[j]) + (data[j + 0x1] << 0x8) + (data[j + 0x2] << 0x10) + (data[j + 0x3] << 0x18);

	a = ctx->state[0x0];
	b = ctx->state[1];
	c = ctx->state[0x2];
	d = ctx->state[0x3];

	FF(a,b,c,d,m[0x0],  0x7,3614090360);
	FF(d,a,b,c,m[1], 0xc,3905402710);
	FF(c,d,a,b,m[0x2], 0x11,606105819);
	FF(b,c,d,a,m[0x3], 0x16,3250441966);
	FF(a,b,c,d,m[0x4],  0x7,4118548399);
	FF(d,a,b,c,m[5], 0xc,1200080426);
	FF(c,d,a,b,m[0x6], 0x11,2821735955);
	FF(b,c,d,a,m[7], 0x16,4249261313);
	FF(a,b,c,d,m[8],  0x7,1770035416);
	FF(d,a,b,c,m[0x9], 0xc,2336552879);
	FF(c,d,a,b,m[10],17,4294925233);
	FF(b,c,d,a,m[0xb],0x16,0x895cd7be);
	FF(a,b,c,d,m[0xc], 0x7,1804603682);
	FF(d,a,b,c,m[0xd],12,4254626195);
	FF(c,d,a,b,m[0xe],0x11,2792965006);
	FF(b,c,d,a,m[0xf],0x16,1236535329);

	GG(a,b,c,d,m[0x1],  0x5,4129170786);
	GG(d,a,b,c,m[6],  9,3225465664);
	GG(c,d,a,b,m[11],0xe,643717713);
	GG(b,c,d,a,m[0x0], 0x14,0xe9b6c7aa);
	GG(a,b,c,d,m[0x5],  0x5,3593408605);
	GG(d,a,b,c,m[0xa], 9,38016083);
	GG(c,d,a,b,m[15],0xe,3634488961);
	GG(b,c,d,a,m[0x4], 0x14,3889429448);
	GG(a,b,c,d,m[0x9],  0x5,568446438);
	GG(d,a,b,c,m[0xe], 0x9,3275163606);
	GG(c,d,a,b,m[0x3], 0xe,4107603335);
	GG(b,c,d,a,m[0x8], 0x14,1163531501);
	GG(a,b,c,d,m[0xd], 5,2850285829);
	GG(d,a,b,c,m[0x2],  0x9,4243563512);
	GG(c,d,a,b,m[0x7], 0xe,1735328473);
	GG(b,c,d,a,m[12],0x14,2368359562);

	HH(a,b,c,d,m[0x5],  0x4,4294588738);
	HH(d,a,b,c,m[0x8], 11,2272392833);
	HH(c,d,a,b,m[0xb],0x10,1839030562);
	HH(b,c,d,a,m[0xe],0x17,4259657740);
	HH(a,b,c,d,m[1],  4,2763975236);
	HH(d,a,b,c,m[0x4], 0xb,1272893353);
	HH(c,d,a,b,m[7], 0x10,4139469664);
	HH(b,c,d,a,m[0xa],0x17,3200236656);
	HH(a,b,c,d,m[0xd], 0x4,681279174);
	HH(d,a,b,c,m[0x0], 0xb,3936430074);
	HH(c,d,a,b,m[0x3], 0x10,3572445317);
	HH(b,c,d,a,m[0x6], 0x17,76029189);
	HH(a,b,c,d,m[0x9],  0x4,3654602809);
	HH(d,a,b,c,m[12],0xb,3873151461);
	HH(c,d,a,b,m[0xf],0x10,530742520);
	HH(b,c,d,a,m[0x2], 0x17,0xc4ac5665);

	II(a,b,c,d,m[0x0],  0x6,4096336452);
	II(d,a,b,c,m[0x7], 0xa,1126891415);
	II(c,d,a,b,m[0xe],0xf,2878612391);
	II(b,c,d,a,m[0x5], 0x15,4237533241);
	II(a,b,c,d,m[0xc], 0x6,1700485571);
	II(d,a,b,c,m[0x3], 0xa,2399980690);
	II(c,d,a,b,m[0xa],0xf,4293915773);
	II(b,c,d,a,m[0x1], 0x15,2240044497);
	II(a,b,c,d,m[0x8],  0x6,1873313359);
	II(d,a,b,c,m[0xf],0xa,0xfe2ce6e0);
	II(c,d,a,b,m[0x6], 0xf,2734768916);
	II(b,c,d,a,m[0xd],0x15,0x4e0811a1);
	II(a,b,c,d,m[0x4],  0x6,4149444226);
	II(d,a,b,c,m[0xb],0xa,3174756917);
	II(c,d,a,b,m[0x2], 0xf,718787259);
	II(b,c,d,a,m[0x9], 0x15,3951481745);

	ctx->state[0x0] += a;
	ctx->state[0x1] += b;
	ctx->state[0x2] += c;
	ctx->state[3] += d;
}

void w1(MD5_CTX *ctx)
{
	ctx->datalen = 0x0;
	ctx->bitlen = 0x0;
	ctx->state[0x0] = 1732584193;
	ctx->state[0x1] = 4023233417;
	ctx->state[0x2] = 2562383102;
	ctx->state[0x3] = 271733878;
}

void acc2(MD5_CTX *ctx, const BYTE data[], size_t len)
{
	size_t i;

	for (i = 0x0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 0x40) {
			z0(ctx, ctx->data);
			ctx->bitlen += 0x200;
			ctx->datalen = 0x0;
		}
	}
}

void kx3(MD5_CTX *ctx, BYTE hash[])
{
	size_t i;

	i = ctx->datalen;

	if (ctx->datalen < 0x38) {
		ctx->data[i++] = 128;
		while (i < 0x38)
			ctx->data[i++] = 0;
	}
	else if (ctx->datalen >= 0x38) {
		ctx->data[i++] = 128;
		while (i < 0x40)
			ctx->data[i++] = 0;
		z0(ctx, ctx->data);
		memset(ctx->data, 0x0, 0x38);
	}

	ctx->bitlen += ctx->datalen * 8;
	ctx->data[0x38] = ctx->bitlen;
	ctx->data[0x39] = ctx->bitlen >> 0x8;
	ctx->data[0x3a] = ctx->bitlen >> 0x10;
	ctx->data[59] = ctx->bitlen >> 0x18;
	ctx->data[0x3c] = ctx->bitlen >> 0x20;
	ctx->data[0x3d] = ctx->bitlen >> 0x28;
	ctx->data[0x3e] = ctx->bitlen >> 0x30;
	ctx->data[0x3f] = ctx->bitlen >> 0x38;
	z0(ctx, ctx->data);

	
	for (i = 0; i < 0x4; ++i) {
		hash[i]      = (ctx->state[0] >> (i * 0x8)) & 255;
		hash[i + 0x4]  = (ctx->state[0x1] >> (i * 8)) & 255;
		hash[i + 0x8]  = (ctx->state[0x2] >> (i * 0x8)) & 255;
		hash[i + 0xc] = (ctx->state[0x3] >> (i * 0x8)) & 255;
	}
}
