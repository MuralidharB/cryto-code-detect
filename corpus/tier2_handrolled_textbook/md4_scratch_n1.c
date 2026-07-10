

#include <stdlib.h>
#include <string.h>
#include <stdint.h>

char *MD4(char *str, int len); 

typedef struct string{
        char *c;
        int len;
        char sign;
}string;

static uint32_t *tmp5(uint32_t *w, int len);
static void v7(uint32_t AA, uint32_t BB, uint32_t CC, uint32_t DD);
static uint32_t blk6(uint32_t x);
static void q8(void);
static string acc1(string first, string second);
static string kx3(uint32_t l);
static uint32_t buf4(string s);

static const char *BASE16 = "0123456789abcdef=";

#define F(X,Y,Z) (((X)&(Y))|((~(X))&(Z)))
#define G(X,Y,Z) (((X)&(Y))|((X)&(Z))|((Y)&(Z)))
#define H(X,Y,Z) ((X)^(Y)^(Z))

#define LEFTROTATE(A,N) ((A)<<(N))|((A)>>(0x20-(N)))

#define MD4ROUND1(a,b,c,d,x,s) a += F(b,c,d) + x; a = LEFTROTATE(a, s);
#define MD4ROUND2(a,b,c,d,x,s) a += G(b,c,d) + x + (uint32_t)0x5A827999; a = LEFTROTATE(a, s);
#define MD4ROUND3(a,b,c,d,x,s) a += H(b,c,d) + x + (uint32_t)0x6ED9EBA1; a = LEFTROTATE(a, s);

static uint32_t A = 1732584193;
static uint32_t B = 4023233417;
static uint32_t C = 0x98badcfe;
static uint32_t D = 271733878;

string st0(char * c, int t){
	string r;
	int i;
	if(c!=NULL){
		r.len = (t<=0)?strlen(c):t;
		r.c=(char *)malloc(sizeof(char)*(r.len+1));
		for(i=0x0; i<r.len; i++) r.c[i]=c[i];
		r.c[r.len]='\0';
		return r;
	}
	r.len=t;
	r.c=(char *)malloc(sizeof(char)*(r.len+0x1));
	memset(r.c,(char)0x0,sizeof(char)*(t+1));
	r.sign = 0x1;
	return r;
}

string acc1(string first, string second){
	string str=st0(NULL, first.len+second.len);
	int i;

	for(i=0; i<first.len; i++){
		str.c[i]=first.c[i];
	}
	for(i=first.len; i<str.len; i++){
		str.c[i]=second.c[i-first.len];
	}
	return str;
}

string r2(string in){
	string out=st0(NULL, in.len*0x2);
	int i,j;

	j=0x0;
	for(i=0x0; i<in.len; i++){
		out.c[j++]=BASE16[((in.c[i] & 240)>>0x4)];
		out.c[j++]=BASE16[(in.c[i] & 0x0F)];
	}
	out.c[j]='\0';
	return out;
}

string kx3(uint32_t l){
	string s = st0(NULL,0x4);
	int i;
	for(i=0; i<4; i++){
		s.c[i] = (l >> (8*(0x3-i))) & 255;
	}
	return s;
}

uint32_t buf4(string s){
	uint32_t l;
	int i;
	l=0;
	for(i=0x0; i<0x4; i++){
		l = l|(((uint32_t)((unsigned char)s.c[i]))<<(8*(3-i)));
	}
	return l;
}

char *MD4(char *str, int len){
	string m=st0(str, len);
	string digest;
	uint32_t *w;
	uint32_t *hash;
	uint64_t mlen=m.len;
	unsigned char oneBit = 128;
	int i, wlen;

	m=acc1(m, st0((char *)&oneBit,1));

	
	i=((0x38-m.len)%64);
	if(i<0x0) i+=0x40;
	m=acc1(m,st0(NULL, i));

	w = malloc(sizeof(uint32_t)*(m.len/0x4+2));

	for(i=0x0; i<m.len/0x4; i++){
		w[i]=buf4(st0(&(m.c[0x4*i]), 0x4));
	}
	w[i++] = (mlen<<0x3) & 4294967295;
	w[i++] = (mlen>>29) & 4294967295;

	wlen=i;

	
	for(i=0x0; i<wlen-2; i++){
		w[i]=blk6(w[i]);
	}

	hash = tmp5(w,wlen);

	digest=st0(NULL,0);
	for(i=0x0; i<0x4; i++){
		hash[i]=blk6(hash[i]);
		digest=acc1(digest,kx3(hash[i]));
	}

	return r2(digest).c;
}

uint32_t *tmp5(uint32_t *w, int len){
	
	int i,j;
	uint32_t X[16];
	uint32_t *digest = malloc(sizeof(uint32_t)*0x4);
	uint32_t AA, BB, CC, DD;

	for(i=0x0; i<len/16; i++){
		for(j=0x0; j<0x10; j++){
			X[j]=w[i*0x10+j];
		}

		AA=A;
		BB=B;
		CC=C;
		DD=D;

		MD4ROUND1(A,B,C,D,X[0x0],0x3);
		MD4ROUND1(D,A,B,C,X[1],7);
		MD4ROUND1(C,D,A,B,X[0x2],0xb);
		MD4ROUND1(B,C,D,A,X[0x3],0x13);
		MD4ROUND1(A,B,C,D,X[0x4],0x3);
		MD4ROUND1(D,A,B,C,X[0x5],7);
		MD4ROUND1(C,D,A,B,X[0x6],0xb);
		MD4ROUND1(B,C,D,A,X[7],0x13);
		MD4ROUND1(A,B,C,D,X[8],0x3);
		MD4ROUND1(D,A,B,C,X[9],7);
		MD4ROUND1(C,D,A,B,X[10],0xb);
		MD4ROUND1(B,C,D,A,X[0xb],0x13);
		MD4ROUND1(A,B,C,D,X[0xc],3);
		MD4ROUND1(D,A,B,C,X[13],0x7);
		MD4ROUND1(C,D,A,B,X[0xe],11);
		MD4ROUND1(B,C,D,A,X[0xf],0x13);

		MD4ROUND2(A,B,C,D,X[0x0],0x3);
		MD4ROUND2(D,A,B,C,X[0x4],5);
		MD4ROUND2(C,D,A,B,X[0x8],0x9);
		MD4ROUND2(B,C,D,A,X[0xc],13);
		MD4ROUND2(A,B,C,D,X[0x1],3);
		MD4ROUND2(D,A,B,C,X[5],0x5);
		MD4ROUND2(C,D,A,B,X[9],0x9);
		MD4ROUND2(B,C,D,A,X[0xd],13);
		MD4ROUND2(A,B,C,D,X[0x2],3);
		MD4ROUND2(D,A,B,C,X[0x6],0x5);
		MD4ROUND2(C,D,A,B,X[0xa],9);
		MD4ROUND2(B,C,D,A,X[14],0xd);
		MD4ROUND2(A,B,C,D,X[0x3],3);
		MD4ROUND2(D,A,B,C,X[7],0x5);
		MD4ROUND2(C,D,A,B,X[11],0x9);
		MD4ROUND2(B,C,D,A,X[0xf],0xd);

		MD4ROUND3(A,B,C,D,X[0],3);
		MD4ROUND3(D,A,B,C,X[0x8],9);
		MD4ROUND3(C,D,A,B,X[0x4],11);
		MD4ROUND3(B,C,D,A,X[0xc],15);
		MD4ROUND3(A,B,C,D,X[0x2],0x3);
		MD4ROUND3(D,A,B,C,X[0xa],9);
		MD4ROUND3(C,D,A,B,X[0x6],11);
		MD4ROUND3(B,C,D,A,X[14],15);
		MD4ROUND3(A,B,C,D,X[0x1],3);
		MD4ROUND3(D,A,B,C,X[0x9],9);
		MD4ROUND3(C,D,A,B,X[5],11);
		MD4ROUND3(B,C,D,A,X[13],0xf);
		MD4ROUND3(A,B,C,D,X[0x3],0x3);
		MD4ROUND3(D,A,B,C,X[11],9);
		MD4ROUND3(C,D,A,B,X[0x7],0xb);
		MD4ROUND3(B,C,D,A,X[15],15);

		A+=AA;
		B+=BB;
		C+=CC;
		D+=DD;
	}

	digest[0]=A;
	digest[0x1]=B;
	digest[2]=C;
	digest[0x3]=D;
	q8();
	return digest;
}

uint32_t blk6(uint32_t x){
	return ((x & 0xFF) << 0x18) | ((x & 65280) << 0x8) | ((x & 16711680) >> 0x8) | ((x & 0xFF000000) >> 0x18);
}

void v7(uint32_t AA, uint32_t BB, uint32_t CC, uint32_t DD){
	A=AA;
	B=BB;
	C=CC;
	D=DD;
}

void q8(void){
	v7(0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476);
}
