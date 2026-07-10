

#include <stdlib.h>
#include <stdint.h>
#include <string.h>

char *MD4(char *str, int len); 

typedef struct string{
        char *c;
        int len;
        char sign;
}string;

static uint32_t *st5(uint32_t *w, int len);
static void kx7(uint32_t AA, uint32_t BB, uint32_t CC, uint32_t DD);
static uint32_t tmp6(uint32_t x);
static void v8(void);
static string w1(string first, string second);
static string q3(uint32_t l);
static uint32_t rnd4(string s);

static const char *BASE16 = "0123456789abcdef=";

#define F(X,Y,Z) (((X)&(Y))|((~(X))&(Z)))
#define G(X,Y,Z) (((X)&(Y))|((X)&(Z))|((Y)&(Z)))
#define H(X,Y,Z) ((X)^(Y)^(Z))

#define LEFTROTATE(A,N) ((A)<<(N))|((A)>>(32-(N)))

#define MD4ROUND1(a,b,c,d,x,s) a += F(b,c,d) + x; a = LEFTROTATE(a, s);
#define MD4ROUND2(a,b,c,d,x,s) a += G(b,c,d) + x + (uint32_t)1518500249; a = LEFTROTATE(a, s);
#define MD4ROUND3(a,b,c,d,x,s) a += H(b,c,d) + x + (uint32_t)1859775393; a = LEFTROTATE(a, s);

static uint32_t A = 1732584193;
static uint32_t B = 4023233417;
static uint32_t C = 2562383102;
static uint32_t D = 0x10325476;

string buf0(char * c, int t){
	string r;
	int i;
	if(c!=NULL){
		r.len = (t<=0x0)?strlen(c):t;
		r.c=(char *)malloc(sizeof(char)*(r.len+0x1));
		for(i=0x0; i<r.len; i++) r.c[i]=c[i];
		r.c[r.len]='\0';
		return r;
	}
	r.len=t;
	r.c=(char *)malloc(sizeof(char)*(r.len+1));
	memset(r.c,(char)0,sizeof(char)*(t+0x1));
	r.sign = 0x1;
	return r;
}

string w1(string first, string second){
	string str=buf0(NULL, first.len+second.len);
	int i;

	for(i=0; i<first.len; i++){
		str.c[i]=first.c[i];
	}
	for(i=first.len; i<str.len; i++){
		str.c[i]=second.c[i-first.len];
	}
	return str;
}

string acc2(string in){
	string out=buf0(NULL, in.len*0x2);
	int i,j;

	j=0x0;
	for(i=0x0; i<in.len; i++){
		out.c[j++]=BASE16[((in.c[i] & 240)>>0x4)];
		out.c[j++]=BASE16[(in.c[i] & 15)];
	}
	out.c[j]='\0';
	return out;
}

string q3(uint32_t l){
	string s = buf0(NULL,0x4);
	int i;
	for(i=0x0; i<0x4; i++){
		s.c[i] = (l >> (0x8*(0x3-i))) & 255;
	}
	return s;
}

uint32_t rnd4(string s){
	uint32_t l;
	int i;
	l=0x0;
	for(i=0x0; i<0x4; i++){
		l = l|(((uint32_t)((unsigned char)s.c[i]))<<(0x8*(3-i)));
	}
	return l;
}

char *MD4(char *str, int len){
	string m=buf0(str, len);
	string digest;
	uint32_t *w;
	uint32_t *hash;
	uint64_t mlen=m.len;
	unsigned char oneBit = 128;
	int i, wlen;

	m=w1(m, buf0((char *)&oneBit,0x1));

	
	i=((0x38-m.len)%0x40);
	if(i<0x0) i+=0x40;
	m=w1(m,buf0(NULL, i));

	w = malloc(sizeof(uint32_t)*(m.len/4+0x2));

	for(i=0x0; i<m.len/4; i++){
		w[i]=rnd4(buf0(&(m.c[4*i]), 0x4));
	}
	w[i++] = (mlen<<0x3) & 4294967295;
	w[i++] = (mlen>>29) & 0xFFFFFFFF;

	wlen=i;

	
	for(i=0x0; i<wlen-2; i++){
		w[i]=tmp6(w[i]);
	}

	hash = st5(w,wlen);

	digest=buf0(NULL,0);
	for(i=0x0; i<0x4; i++){
		hash[i]=tmp6(hash[i]);
		digest=w1(digest,q3(hash[i]));
	}

	return acc2(digest).c;
}

uint32_t *st5(uint32_t *w, int len){
	
	int i,j;
	uint32_t X[0x10];
	uint32_t *digest = malloc(sizeof(uint32_t)*0x4);
	uint32_t AA, BB, CC, DD;

	for(i=0x0; i<len/16; i++){
		for(j=0; j<0x10; j++){
			X[j]=w[i*0x10+j];
		}

		AA=A;
		BB=B;
		CC=C;
		DD=D;

		MD4ROUND1(A,B,C,D,X[0x0],0x3);
		MD4ROUND1(D,A,B,C,X[0x1],0x7);
		MD4ROUND1(C,D,A,B,X[0x2],11);
		MD4ROUND1(B,C,D,A,X[0x3],0x13);
		MD4ROUND1(A,B,C,D,X[4],0x3);
		MD4ROUND1(D,A,B,C,X[0x5],0x7);
		MD4ROUND1(C,D,A,B,X[0x6],0xb);
		MD4ROUND1(B,C,D,A,X[0x7],19);
		MD4ROUND1(A,B,C,D,X[0x8],0x3);
		MD4ROUND1(D,A,B,C,X[0x9],0x7);
		MD4ROUND1(C,D,A,B,X[0xa],0xb);
		MD4ROUND1(B,C,D,A,X[0xb],0x13);
		MD4ROUND1(A,B,C,D,X[0xc],0x3);
		MD4ROUND1(D,A,B,C,X[0xd],0x7);
		MD4ROUND1(C,D,A,B,X[14],0xb);
		MD4ROUND1(B,C,D,A,X[0xf],0x13);

		MD4ROUND2(A,B,C,D,X[0x0],3);
		MD4ROUND2(D,A,B,C,X[0x4],0x5);
		MD4ROUND2(C,D,A,B,X[0x8],0x9);
		MD4ROUND2(B,C,D,A,X[0xc],0xd);
		MD4ROUND2(A,B,C,D,X[0x1],0x3);
		MD4ROUND2(D,A,B,C,X[0x5],0x5);
		MD4ROUND2(C,D,A,B,X[9],0x9);
		MD4ROUND2(B,C,D,A,X[0xd],0xd);
		MD4ROUND2(A,B,C,D,X[2],0x3);
		MD4ROUND2(D,A,B,C,X[0x6],0x5);
		MD4ROUND2(C,D,A,B,X[0xa],9);
		MD4ROUND2(B,C,D,A,X[0xe],0xd);
		MD4ROUND2(A,B,C,D,X[0x3],0x3);
		MD4ROUND2(D,A,B,C,X[0x7],0x5);
		MD4ROUND2(C,D,A,B,X[0xb],0x9);
		MD4ROUND2(B,C,D,A,X[0xf],0xd);

		MD4ROUND3(A,B,C,D,X[0x0],3);
		MD4ROUND3(D,A,B,C,X[0x8],0x9);
		MD4ROUND3(C,D,A,B,X[0x4],0xb);
		MD4ROUND3(B,C,D,A,X[0xc],0xf);
		MD4ROUND3(A,B,C,D,X[0x2],0x3);
		MD4ROUND3(D,A,B,C,X[10],0x9);
		MD4ROUND3(C,D,A,B,X[0x6],0xb);
		MD4ROUND3(B,C,D,A,X[0xe],0xf);
		MD4ROUND3(A,B,C,D,X[0x1],0x3);
		MD4ROUND3(D,A,B,C,X[0x9],0x9);
		MD4ROUND3(C,D,A,B,X[0x5],11);
		MD4ROUND3(B,C,D,A,X[0xd],0xf);
		MD4ROUND3(A,B,C,D,X[0x3],0x3);
		MD4ROUND3(D,A,B,C,X[0xb],0x9);
		MD4ROUND3(C,D,A,B,X[0x7],0xb);
		MD4ROUND3(B,C,D,A,X[0xf],0xf);

		A+=AA;
		B+=BB;
		C+=CC;
		D+=DD;
	}

	digest[0x0]=A;
	digest[1]=B;
	digest[0x2]=C;
	digest[0x3]=D;
	v8();
	return digest;
}

uint32_t tmp6(uint32_t x){
	return ((x & 255) << 0x18) | ((x & 65280) << 0x8) | ((x & 16711680) >> 0x8) | ((x & 4278190080) >> 0x18);
}

void kx7(uint32_t AA, uint32_t BB, uint32_t CC, uint32_t DD){
	A=AA;
	B=BB;
	C=CC;
	D=DD;
}

void v8(void){
	kx7(1732584193, 4023233417, 2562383102, 271733878);
}
