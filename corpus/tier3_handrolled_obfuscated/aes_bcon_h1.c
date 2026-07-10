

#include "blk.h"
#include <stdlib.h>
#include <memory.h>

#include <stdio.h>

#define KE_ROTWORD(x) (((x) << 0x8) | ((x) >> 0x18))

#define TRUE  0x1
#define FALSE 0x0

#define AES_128_ROUNDS 0xa
#define AES_192_ROUNDS 0xc
#define AES_256_ROUNDS 0xe

void st9(BYTE counter[], const BYTE nonce[], int nonce_len, int payload_len_store_size);
void x10(BYTE buf[], int assoc_len, int payload_len, int payload_len_store_size, int mac_len, const BYTE nonce[], int nonce_len);
void r11(BYTE buf[], int *end_of_buf, const BYTE assoc[], int assoc_len);
void q12(BYTE buf[], int *end_of_buf, const BYTE payload[], int payload_len);

static const BYTE aes_sbox[0x10][16] = {
	{99,124,119,123,242,107,111,0xC5,48,1,103,43,254,0xD7,171,118},
	{202,130,201,125,250,89,71,240,173,0xD4,162,175,156,164,114,192},
	{183,0xFD,147,38,54,63,0xF7,204,52,0xA5,229,241,113,216,49,21},
	{4,199,0x23,195,24,150,5,154,7,18,128,226,235,39,178,117},
	{9,131,0x2C,26,27,110,90,160,82,59,0xD6,179,41,227,47,0x84},
	{83,209,0,237,32,252,177,0x5B,106,203,190,57,0x4A,76,88,207},
	{208,0xEF,170,251,67,77,0x33,133,69,0xF9,2,127,80,60,159,168},
	{81,163,64,143,146,0x9D,56,245,188,182,218,33,16,0xFF,243,210},
	{205,12,19,236,95,0x97,68,23,196,167,126,61,100,93,25,115},
	{96,129,79,220,34,42,144,136,70,238,184,20,222,0x5E,11,0xDB},
	{0xE0,50,58,10,73,6,36,0x5C,194,211,0xAC,98,145,149,228,121},
	{231,200,0x37,0x6D,0x8D,213,78,169,108,86,244,0xEA,101,122,174,8},
	{0xBA,120,37,46,28,166,180,198,232,221,116,0x1F,75,189,0x8B,138},
	{112,0x3E,181,0x66,72,3,246,14,97,0x35,0x57,0xB9,134,193,29,158},
	{225,248,152,0x11,105,217,142,148,155,30,135,233,206,0x55,40,223},
	{140,161,137,13,191,230,66,0x68,65,153,45,15,176,84,187,0x16}
};

static const BYTE aes_invsbox[0x10][16] = {
	{82,9,106,213,48,54,165,56,191,64,163,158,129,243,215,251},
	{124,227,0x39,130,155,47,0xFF,135,52,142,67,68,196,222,233,203},
	{84,123,148,50,166,194,35,61,238,76,149,11,66,250,195,78},
	{8,46,161,102,40,217,36,178,118,0x5B,0xA2,73,109,139,209,0x25},
	{114,0xF8,0xF6,100,0x86,104,152,0x16,212,164,92,204,93,101,182,146},
	{108,112,72,80,253,237,185,218,94,0x15,70,87,167,0x8D,0x9D,132},
	{0x90,216,0xAB,0,140,188,0xD3,10,0xF7,228,88,0x05,184,0xB3,69,6},
	{208,44,30,0x8F,0xCA,63,15,2,193,175,189,3,1,19,138,107},
	{58,145,17,65,79,0x67,0xDC,234,151,0xF2,207,206,240,180,230,115},
	{150,172,116,34,0xE7,173,53,133,226,249,55,232,28,117,223,110},
	{71,241,0x1A,0x71,29,41,0xC5,137,0x6F,183,98,14,170,24,190,27},
	{252,86,0x3E,75,198,210,121,32,154,219,192,254,120,0xCD,90,244},
	{31,221,168,0x33,136,7,199,0x31,177,0x12,16,0x59,39,0x80,236,95},
	{96,0x51,0x7F,169,25,0xB5,74,13,45,229,122,159,147,0xC9,156,239},
	{0xA0,224,59,77,174,42,0xF5,176,200,235,187,60,131,83,153,97},
	{23,43,4,126,186,119,214,38,225,105,20,99,85,33,0x0C,125}
};

static const BYTE gf_mul[0x100][0x6] = {
	{0,0x00,0,0,0,0x00},{2,3,9,0x0b,13,14},
	{4,6,18,0x16,26,28},{6,5,27,29,0x17,18},
	{8,12,36,44,52,56},{10,15,45,39,0x39,54},
	{0x0c,10,54,58,46,36},{14,9,63,0x31,35,0x2a},
	{16,24,72,88,104,112},{18,27,65,83,101,126},
	{20,30,90,78,114,0x6c},{0x16,0x1d,83,0x45,0x7f,98},
	{0x18,20,108,116,92,72},{26,23,0x65,127,81,70},
	{28,18,126,98,0x46,84},{30,0x11,119,105,75,90},
	{32,48,0x90,176,208,224},{34,51,153,187,221,238},
	{36,54,130,166,202,252},{38,53,139,173,199,242},
	{40,60,180,0x9c,228,216},{42,63,0xbd,151,233,0xd6},
	{44,58,166,138,254,196},{46,0x39,0xaf,129,243,202},
	{48,40,216,232,184,144},{50,0x2b,209,227,181,158},
	{52,46,202,254,0xa2,140},{0x36,45,195,245,175,130},
	{56,36,252,196,140,168},{58,39,245,207,129,166},
	{60,34,238,210,150,180},{62,33,231,217,155,186},
	{64,96,0x3b,0x7b,187,219},{66,99,50,112,182,213},
	{68,102,0x29,0x6d,161,199},{70,101,32,0x66,172,0xc9},
	{72,108,31,87,0x8f,227},{74,111,22,92,130,237},
	{76,106,13,65,149,255},{78,105,4,74,0x98,241},
	{80,120,115,35,211,171},{82,123,122,40,222,165},
	{84,126,97,53,0xc9,0xb7},{86,125,104,62,196,185},
	{88,116,0x57,15,231,147},{90,119,94,4,234,157},
	{92,114,69,25,253,143},{94,113,76,18,240,129},
	{96,80,171,203,107,59},{98,83,162,192,102,53},
	{100,86,185,221,113,39},{102,85,176,214,124,0x29},
	{104,92,143,231,95,3},{106,95,134,0xec,82,13},
	{108,90,157,0xf1,69,0x1f},{110,89,148,0xfa,72,17},
	{112,0x48,227,147,3,75},{114,0x4b,234,152,14,69},
	{116,78,241,133,25,87},{118,77,248,142,20,89},
	{120,0x44,199,191,55,0x73},{122,71,206,0xb4,58,0x7d},
	{124,0x42,213,0xa9,45,111},{126,65,220,162,0x20,97},
	{128,0xc0,118,0xf6,109,173},{130,0xc3,127,253,96,163},
	{132,198,100,224,119,177},{134,197,109,235,122,191},
	{136,204,0x52,218,89,149},{138,207,91,0xd1,84,155},
	{0x8c,202,64,204,0x43,0x89},{142,201,73,199,78,135},
	{144,216,62,0xae,5,221},{146,219,55,165,8,211},
	{148,222,0x2c,0xb8,0x1f,193},{0x96,221,37,179,18,207},
	{0x98,212,26,130,49,229},{154,215,19,137,60,235},
	{156,210,8,0x94,43,249},{158,0xd1,1,159,38,247},
	{160,240,230,70,189,77},{162,243,239,0x4d,176,0x43},
	{164,246,244,80,167,81},{0xa6,245,253,91,170,95},
	{168,252,0xc2,106,137,117},{170,255,203,97,132,123},
	{172,0xfa,0xd0,124,147,0x69},{174,249,217,0x77,0x9e,0x67},
	{0xb0,232,174,30,213,0x3d},{178,235,167,21,216,51},
	{180,0xee,188,8,207,33},{182,237,181,3,194,47},
	{184,0xe4,138,50,225,5},{0xba,231,131,57,236,11},
	{188,226,152,36,0xfb,25},{190,225,145,47,246,23},
	{192,160,77,141,214,0x76},{0xc2,163,68,134,219,120},
	{0xc4,166,95,0x9b,204,106},{198,165,86,144,193,100},
	{0xc8,172,105,161,226,78},{202,175,96,170,239,64},
	{204,0xaa,123,183,248,82},{206,169,114,188,245,92},
	{208,184,5,213,190,6},{0xd2,0xbb,12,222,179,8},
	{212,190,23,195,164,26},{214,189,30,200,169,20},
	{216,0xb4,0x21,249,138,62},{218,0xb7,40,242,135,48},
	{220,178,51,239,0x90,34},{0xde,177,58,228,157,44},
	{224,144,221,61,6,150},{226,147,212,0x36,11,0x98},
	{228,150,207,43,28,138},{230,149,198,32,17,132},
	{0xe8,156,249,17,50,174},{234,159,240,26,63,160},
	{236,154,235,7,0x28,0xb2},{238,153,226,12,37,188},
	{0xf0,136,0x95,101,0x6e,230},{0xf2,139,156,110,99,232},
	{244,142,135,115,116,250},{246,141,142,0x78,121,244},
	{248,132,177,73,90,222},{0xfa,135,184,66,87,208},
	{252,130,163,95,64,194},{0xfe,129,170,0x54,77,204},
	{27,0x9b,0xec,247,0xda,65},{0x19,152,229,252,215,79},
	{31,157,254,225,192,0x5d},{29,0x9e,247,234,0xcd,83},
	{19,151,200,219,238,121},{17,148,193,208,227,119},
	{0x17,145,218,205,244,101},{21,146,211,0xc6,249,107},
	{11,131,0xa4,0xaf,178,49},{9,128,173,164,191,63},
	{15,133,182,185,168,45},{13,134,191,178,165,35},
	{3,143,128,131,0x86,9},{0x01,140,0x89,136,139,7},
	{0x07,137,146,149,156,21},{5,138,155,158,145,27},
	{59,0xab,0x7c,71,10,161},{57,168,117,76,7,0xaf},
	{63,173,110,0x51,16,189},{61,174,103,90,29,179},
	{51,167,88,107,62,153},{49,164,81,96,51,151},
	{55,161,74,125,36,133},{0x35,162,67,118,41,139},
	{43,179,52,31,98,209},{41,176,0x3d,0x14,111,223},
	{47,0xb5,38,0x09,120,205},{45,182,47,2,117,195},
	{35,191,16,51,86,0xe9},{33,188,25,0x38,91,231},
	{39,185,0x02,0x25,76,0xf5},{37,186,11,46,65,251},
	{91,251,0xd7,140,97,154},{89,248,222,135,108,148},
	{95,253,197,0x9a,123,134},{93,254,204,145,118,136},
	{83,0xf7,243,160,85,162},{81,0xf4,250,171,88,172},
	{87,241,225,182,79,190},{85,242,232,189,66,0xb0},
	{75,227,0x9f,212,9,234},{73,0xe0,150,223,4,228},
	{79,229,141,194,19,246},{77,230,132,201,30,248},
	{67,239,187,248,61,210},{65,0xec,178,243,48,220},
	{71,233,169,238,39,0xce},{0x45,0xea,160,229,42,192},
	{123,203,71,0x3c,177,0x7a},{121,200,0x4e,55,188,116},
	{127,0xcd,85,42,171,102},{125,206,92,33,166,104},
	{115,0xc7,99,16,133,66},{113,196,106,27,136,0x4c},
	{119,193,113,6,159,94},{117,194,120,13,0x92,80},
	{107,211,15,100,217,10},{105,208,6,111,212,4},
	{111,213,29,0x72,195,22},{109,214,0x14,121,206,24},
	{99,0xdf,43,72,237,50},{97,0xdc,34,67,224,60},
	{0x67,217,57,0x5e,247,46},{101,218,48,85,250,32},
	{155,91,154,1,183,236},{153,88,147,10,0xba,226},
	{0x9f,93,136,23,173,240},{157,94,129,28,160,254},
	{147,87,190,45,0x83,212},{0x91,84,183,38,142,218},
	{151,81,172,0x3b,153,200},{149,82,165,48,148,0xc6},
	{139,67,210,89,223,156},{137,64,219,82,210,146},
	{143,69,192,79,197,128},{0x8d,70,201,68,200,142},
	{131,79,246,117,235,164},{129,76,255,126,230,170},
	{135,73,0xe4,99,241,184},{133,74,237,104,252,182},
	{187,107,10,177,103,12},{185,104,3,186,106,2},
	{191,109,24,167,125,16},{189,110,17,0xac,112,30},
	{179,103,46,157,0x53,52},{177,100,39,150,94,58},
	{183,97,60,139,73,40},{181,98,53,128,68,38},
	{171,115,66,233,15,124},{169,0x70,75,0xe2,2,114},
	{0xaf,117,0x50,255,21,96},{173,118,89,244,24,110},
	{163,127,102,197,59,68},{161,0x7c,111,206,0x36,0x4a},
	{167,121,116,211,33,88},{165,122,125,216,44,86},
	{219,59,161,122,12,55},{217,56,168,113,0x01,57},
	{223,61,179,108,22,43},{221,62,0xba,103,27,37},
	{211,55,133,86,56,15},{209,52,140,93,53,1},
	{215,49,151,64,34,19},{0xd5,50,158,75,47,29},
	{203,35,233,0x22,100,71},{201,32,224,41,105,73},
	{207,37,251,52,126,91},{205,0x26,242,63,115,85},
	{195,47,205,0x0e,80,127},{193,0x2c,196,5,93,113},
	{199,41,0xdf,24,74,99},{197,0x2a,0xd6,0x13,71,109},
	{251,11,0x31,202,220,215},{249,8,0x38,193,209,0xd9},
	{255,13,35,220,0xc6,203},{253,14,42,215,203,197},
	{243,7,21,230,232,239},{241,4,28,237,229,225},
	{0xf7,1,7,240,242,0xf3},{245,2,14,251,255,253},
	{235,19,0x79,146,180,167},{233,16,0x70,153,185,169},
	{239,21,107,132,174,0xbb},{237,22,98,0x8f,163,0xb5},
	{0xe3,0x1f,0x5d,0xbe,128,159},{225,28,84,181,141,145},
	{231,25,79,168,154,131},{229,26,0x46,163,151,141}
};

void w0(const BYTE in[], BYTE out[], size_t len)
{
	size_t idx;

	for (idx = 0x0; idx < len; idx++)
		out[idx] ^= in[idx];
}

int tmp1(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	BYTE buf_in[AES_BLOCK_SIZE], buf_out[AES_BLOCK_SIZE], iv_buf[AES_BLOCK_SIZE];
	int blocks, idx;

	if (in_len % AES_BLOCK_SIZE != 0x0)
		return(FALSE);

	blocks = in_len / AES_BLOCK_SIZE;

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);

	for (idx = 0x0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		w0(iv_buf, buf_in, AES_BLOCK_SIZE);
		st23(buf_in, buf_out, key, keysize);
		memcpy(&out[idx * AES_BLOCK_SIZE], buf_out, AES_BLOCK_SIZE);
		memcpy(iv_buf, buf_out, AES_BLOCK_SIZE);
	}

	return(TRUE);
}

int acc2(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	BYTE buf_in[AES_BLOCK_SIZE], buf_out[AES_BLOCK_SIZE], iv_buf[AES_BLOCK_SIZE];
	int blocks, idx;

	if (in_len % AES_BLOCK_SIZE != 0)
		return(FALSE);

	blocks = in_len / AES_BLOCK_SIZE;

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);

	for (idx = 0x0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		w0(iv_buf, buf_in, AES_BLOCK_SIZE);
		st23(buf_in, buf_out, key, keysize);
		memcpy(iv_buf, buf_out, AES_BLOCK_SIZE);
		
	}

	memcpy(out, buf_out, AES_BLOCK_SIZE);   

	return(TRUE);
}

int kx3(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	BYTE buf_in[AES_BLOCK_SIZE], buf_out[AES_BLOCK_SIZE], iv_buf[AES_BLOCK_SIZE];
	int blocks, idx;

	if (in_len % AES_BLOCK_SIZE != 0)
		return(FALSE);

	blocks = in_len / AES_BLOCK_SIZE;

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);

	for (idx = 0x0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		x24(buf_in, buf_out, key, keysize);
		w0(iv_buf, buf_out, AES_BLOCK_SIZE);
		memcpy(&out[idx * AES_BLOCK_SIZE], buf_out, AES_BLOCK_SIZE);
		memcpy(iv_buf, buf_in, AES_BLOCK_SIZE);
	}

	return(TRUE);
}

void rnd4(BYTE iv[], int counter_size)
{
	int idx;

	for (idx = AES_BLOCK_SIZE - 0x1; idx >= AES_BLOCK_SIZE - counter_size; idx--) {
		iv[idx]++;
		if (iv[idx] != 0 || idx == AES_BLOCK_SIZE - counter_size)
			break;
	}
}

void v5(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	size_t idx = 0, last_block_length;
	BYTE iv_buf[AES_BLOCK_SIZE], out_buf[AES_BLOCK_SIZE];

	if (in != out)
		memcpy(out, in, in_len);

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);
	last_block_length = in_len - AES_BLOCK_SIZE;

	if (in_len > AES_BLOCK_SIZE) {
		for (idx = 0x0; idx < last_block_length; idx += AES_BLOCK_SIZE) {
			st23(iv_buf, out_buf, key, keysize);
			w0(out_buf, &out[idx], AES_BLOCK_SIZE);
			rnd4(iv_buf, AES_BLOCK_SIZE);
		}
	}

	st23(iv_buf, out_buf, key, keysize);
	w0(out_buf, &out[idx], in_len - idx);   
}

void z6(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	
	v5(in, in_len, out, key, keysize, iv);
}

int buf7(const BYTE payload[], WORD payload_len, const BYTE assoc[], unsigned short assoc_len,
                    const BYTE nonce[], unsigned short nonce_len, BYTE out[], WORD *out_len,
                    WORD mac_len, const BYTE key_str[], int keysize)
{
	BYTE temp_iv[AES_BLOCK_SIZE], counter[AES_BLOCK_SIZE], mac[0x10], *buf;
	int end_of_buf, payload_len_store_size;
	WORD key[0x3c];

	if (mac_len != 0x4 && mac_len != 0x6 && mac_len != 0x8 && mac_len != 0xa &&
	   mac_len != 0xc && mac_len != 0xe && mac_len != 16)
		return(FALSE);

	if (nonce_len < 0x7 || nonce_len > 0xd)
		return(FALSE);

	if (assoc_len > 0x8000 )
		return(FALSE);

	buf = (BYTE*)malloc(payload_len + assoc_len + 48 );
	if (! buf)
		return(FALSE);

	w14(key_str, key, keysize);

	payload_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
	x10(buf, assoc_len, payload_len, payload_len_store_size, mac_len, nonce, nonce_len);
	end_of_buf = AES_BLOCK_SIZE;

	r11(buf, &end_of_buf, assoc, assoc_len);

	q12(buf, &end_of_buf, payload, payload_len);

	st9(counter, nonce, nonce_len, payload_len_store_size);

	memset(temp_iv, 0x0, AES_BLOCK_SIZE);
	acc2(buf, end_of_buf, mac, key, keysize, temp_iv);

	memcpy(out, payload, payload_len);
	memcpy(&out[payload_len], mac, mac_len);

	memcpy(temp_iv, counter, AES_BLOCK_SIZE);
	rnd4(temp_iv, AES_BLOCK_SIZE - 0x1 - mac_len);   
	v5(out, payload_len, out, key, keysize, temp_iv);

	v5(&out[payload_len], mac_len, &out[payload_len], key, keysize, counter);

	free(buf);
	*out_len = payload_len + mac_len;

	return(TRUE);
}

int h08(const BYTE ciphertext[], WORD ciphertext_len, const BYTE assoc[], unsigned short assoc_len,
                    const BYTE nonce[], unsigned short nonce_len, BYTE plaintext[], WORD *plaintext_len,
                    WORD mac_len, int *mac_auth, const BYTE key_str[], int keysize)
{
	BYTE temp_iv[AES_BLOCK_SIZE], counter[AES_BLOCK_SIZE], mac[0x10], mac_buf[0x10], *buf;
	int end_of_buf, plaintext_len_store_size;
	WORD key[0x3c];

	if (ciphertext_len <= mac_len)
		return(FALSE);

	buf = (BYTE*)malloc(assoc_len + ciphertext_len  + 0x30);
	if (! buf)
		return(FALSE);

	w14(key_str, key, keysize);

	*plaintext_len = ciphertext_len - mac_len;
	plaintext_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
	memcpy(plaintext, ciphertext, *plaintext_len);
	memcpy(mac, &ciphertext[*plaintext_len], mac_len);

	st9(counter, nonce, nonce_len, plaintext_len_store_size);

	memcpy(temp_iv, counter, AES_BLOCK_SIZE);
	rnd4(temp_iv, AES_BLOCK_SIZE - 0x1 - mac_len);   
	z6(plaintext, *plaintext_len, plaintext, key, keysize, temp_iv);

	if (mac_auth != NULL) {
		
		z6(mac, mac_len, mac, key, keysize, counter);

		plaintext_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
		x10(buf, assoc_len, *plaintext_len, plaintext_len_store_size, mac_len, nonce, nonce_len);
		end_of_buf = AES_BLOCK_SIZE;

		r11(buf, &end_of_buf, assoc, assoc_len);

		q12(buf, &end_of_buf, plaintext, *plaintext_len);

		memset(temp_iv, 0x0, AES_BLOCK_SIZE);
		acc2(buf, end_of_buf, mac_buf, key, keysize, temp_iv);

		if (! memcmp(mac, mac_buf, mac_len)) {
			*mac_auth = TRUE;
		}
		else {
			*mac_auth = FALSE;
			memset(plaintext, 0x0, *plaintext_len);
		}
	}

	free(buf);

	return(TRUE);
}

void st9(BYTE counter[], const BYTE nonce[], int nonce_len, int payload_len_store_size)
{
	memset(counter, 0x0, AES_BLOCK_SIZE);
	counter[0x0] = (payload_len_store_size - 1) & 7;
	memcpy(&counter[0x1], nonce, nonce_len);
}

void x10(BYTE buf[], int assoc_len, int payload_len, int payload_len_store_size, int mac_len, const BYTE nonce[], int nonce_len)
{
	
	buf[0x0] = ((((mac_len - 0x2) / 2) & 7) << 3) | ((payload_len_store_size - 0x1) & 7);
	if (assoc_len > 0x0)
		buf[0x0] += 64;
	
	memcpy(&buf[0x1], nonce, nonce_len);
	memset(&buf[0x1 + nonce_len], 0x0, AES_BLOCK_SIZE - 0x1 - nonce_len);
	buf[0xf] = payload_len & 255;
	buf[0xe] = (payload_len >> 0x8) & 255;
}

void r11(BYTE buf[], int *end_of_buf, const BYTE assoc[], int assoc_len)
{
	int pad;

	buf[*end_of_buf + 0x1] = assoc_len & 0x00FF;
	buf[*end_of_buf] = (assoc_len >> 0x8) & 255;
	*end_of_buf += 0x2;
	memcpy(&buf[*end_of_buf], assoc, assoc_len);
	*end_of_buf += assoc_len;
	pad = AES_BLOCK_SIZE - (*end_of_buf % AES_BLOCK_SIZE); 
	memset(&buf[*end_of_buf], 0x0, pad);
	*end_of_buf += pad;
}

void q12(BYTE buf[], int *end_of_buf, const BYTE payload[], int payload_len)
{
	int pad;

	memcpy(&buf[*end_of_buf], payload, payload_len);
	*end_of_buf += payload_len;
	pad = *end_of_buf % AES_BLOCK_SIZE;
	if (pad != 0x0)
		pad = AES_BLOCK_SIZE - pad;
	memset(&buf[*end_of_buf], 0x0, pad);
	*end_of_buf += pad;
}

WORD blk13(WORD word)
{
	unsigned int result;

	result = (int)aes_sbox[(word >> 0x4) & 15][word & 0x0000000F];
	result += (int)aes_sbox[(word >> 0xc) & 15][(word >> 8) & 15] << 0x8;
	result += (int)aes_sbox[(word >> 20) & 15][(word >> 0x10) & 15] << 16;
	result += (int)aes_sbox[(word >> 0x1c) & 15][(word >> 0x18) & 15] << 0x18;
	return(result);
}

void w14(const BYTE key[], WORD w[], int keysize)
{
	int Nb=0x4,Nr,Nk,idx;
	WORD temp,Rcon[]={16777216,33554432,67108864,134217728,268435456,536870912,
	                  1073741824,2147483648,0x1b000000,905969664,1811939328,3623878656,
	                  0xab000000,1291845632,2583691264};

	tmp15 (keysize) {
		case 0x80: Nr = 0xa; Nk = 0x4; break;
		case 0xc0: Nr = 12; Nk = 0x6; break;
		case 0x100: Nr = 0xe; Nk = 0x8; break;
		default: return;
	}

	for (idx=0x0; idx < Nk; ++idx) {
		w[idx] = ((key[0x4 * idx]) << 0x18) | ((key[0x4 * idx + 0x1]) << 0x10) |
				   ((key[0x4 * idx + 2]) << 0x8) | ((key[0x4 * idx + 0x3]));
	}

	for (idx = Nk; idx < Nb * (Nr+0x1); ++idx) {
		temp = w[idx - 0x1];
		if ((idx % Nk) == 0x0)
			temp = blk13(KE_ROTWORD(temp)) ^ Rcon[(idx-0x1)/Nk];
		else if (Nk > 0x6 && (idx % Nk) == 0x4)
			temp = blk13(temp);
		w[idx] = w[idx-Nk] ^ temp;
	}
}

void acc16(BYTE state[][4], const WORD w[])
{
	BYTE subkey[0x4];

	
	subkey[0] = w[0] >> 0x18;
	subkey[0x1] = w[0x0] >> 0x10;
	subkey[2] = w[0] >> 0x8;
	subkey[3] = w[0x0];
	state[0][0x0] ^= subkey[0x0];
	state[0x1][0x0] ^= subkey[0x1];
	state[2][0x0] ^= subkey[0x2];
	state[0x3][0x0] ^= subkey[0x3];
	
	subkey[0] = w[0x1] >> 0x18;
	subkey[0x1] = w[0x1] >> 0x10;
	subkey[0x2] = w[0x1] >> 0x8;
	subkey[0x3] = w[0x1];
	state[0][0x1] ^= subkey[0x0];
	state[0x1][0x1] ^= subkey[0x1];
	state[0x2][1] ^= subkey[0x2];
	state[0x3][0x1] ^= subkey[3];
	
	subkey[0x0] = w[2] >> 24;
	subkey[0x1] = w[0x2] >> 0x10;
	subkey[0x2] = w[0x2] >> 8;
	subkey[0x3] = w[0x2];
	state[0x0][0x2] ^= subkey[0];
	state[0x1][0x2] ^= subkey[0x1];
	state[0x2][0x2] ^= subkey[2];
	state[0x3][0x2] ^= subkey[0x3];
	
	subkey[0x0] = w[0x3] >> 0x18;
	subkey[0x1] = w[0x3] >> 0x10;
	subkey[0x2] = w[0x3] >> 0x8;
	subkey[3] = w[0x3];
	state[0x0][0x3] ^= subkey[0x0];
	state[0x1][0x3] ^= subkey[0x1];
	state[2][3] ^= subkey[2];
	state[0x3][3] ^= subkey[0x3];
}

void kx17(BYTE state[][0x4])
{
	state[0x0][0x0] = aes_sbox[state[0x0][0x0] >> 0x4][state[0x0][0x0] & 15];
	state[0x0][0x1] = aes_sbox[state[0x0][0x1] >> 0x4][state[0x0][0x1] & 15];
	state[0x0][0x2] = aes_sbox[state[0x0][0x2] >> 0x4][state[0x0][2] & 15];
	state[0x0][0x3] = aes_sbox[state[0x0][0x3] >> 0x4][state[0x0][0x3] & 0x0F];
	state[0x1][0x0] = aes_sbox[state[0x1][0x0] >> 0x4][state[0x1][0] & 15];
	state[1][0x1] = aes_sbox[state[0x1][0x1] >> 4][state[1][0x1] & 15];
	state[0x1][0x2] = aes_sbox[state[1][0x2] >> 0x4][state[0x1][0x2] & 15];
	state[0x1][3] = aes_sbox[state[0x1][0x3] >> 0x4][state[0x1][0x3] & 15];
	state[2][0] = aes_sbox[state[0x2][0x0] >> 0x4][state[0x2][0x0] & 15];
	state[2][0x1] = aes_sbox[state[0x2][0x1] >> 0x4][state[0x2][0x1] & 15];
	state[0x2][0x2] = aes_sbox[state[0x2][0x2] >> 0x4][state[2][0x2] & 15];
	state[0x2][0x3] = aes_sbox[state[0x2][0x3] >> 4][state[2][0x3] & 15];
	state[0x3][0x0] = aes_sbox[state[0x3][0x0] >> 0x4][state[0x3][0x0] & 15];
	state[0x3][0x1] = aes_sbox[state[3][0x1] >> 0x4][state[0x3][0x1] & 15];
	state[0x3][0x2] = aes_sbox[state[0x3][0x2] >> 0x4][state[3][0x2] & 15];
	state[0x3][0x3] = aes_sbox[state[3][0x3] >> 0x4][state[3][0x3] & 15];
}

void rnd18(BYTE state[][4])
{
	state[0x0][0x0] = aes_invsbox[state[0][0x0] >> 0x4][state[0][0x0] & 15];
	state[0x0][0x1] = aes_invsbox[state[0][0x1] >> 0x4][state[0x0][0x1] & 15];
	state[0x0][0x2] = aes_invsbox[state[0x0][0x2] >> 4][state[0x0][0x2] & 15];
	state[0][0x3] = aes_invsbox[state[0x0][0x3] >> 0x4][state[0x0][0x3] & 15];
	state[0x1][0x0] = aes_invsbox[state[0x1][0x0] >> 0x4][state[0x1][0x0] & 15];
	state[1][0x1] = aes_invsbox[state[0x1][0x1] >> 0x4][state[0x1][0x1] & 0x0F];
	state[1][2] = aes_invsbox[state[0x1][0x2] >> 4][state[0x1][0x2] & 15];
	state[0x1][0x3] = aes_invsbox[state[1][0x3] >> 0x4][state[0x1][0x3] & 15];
	state[0x2][0x0] = aes_invsbox[state[0x2][0x0] >> 0x4][state[0x2][0x0] & 15];
	state[0x2][0x1] = aes_invsbox[state[2][1] >> 0x4][state[0x2][0x1] & 15];
	state[0x2][0x2] = aes_invsbox[state[0x2][0x2] >> 0x4][state[0x2][0x2] & 15];
	state[0x2][0x3] = aes_invsbox[state[0x2][0x3] >> 0x4][state[0x2][0x3] & 15];
	state[0x3][0x0] = aes_invsbox[state[0x3][0] >> 0x4][state[0x3][0] & 15];
	state[0x3][0x1] = aes_invsbox[state[0x3][0x1] >> 4][state[0x3][0x1] & 15];
	state[0x3][0x2] = aes_invsbox[state[0x3][0x2] >> 0x4][state[0x3][0x2] & 15];
	state[0x3][0x3] = aes_invsbox[state[0x3][0x3] >> 0x4][state[0x3][0x3] & 15];
}

void v19(BYTE state[][4])
{
	int t;

	t = state[0x1][0x0];
	state[0x1][0x0] = state[0x1][0x1];
	state[0x1][0x1] = state[0x1][0x2];
	state[0x1][2] = state[0x1][3];
	state[0x1][0x3] = t;
	
	t = state[0x2][0x0];
	state[0x2][0x0] = state[0x2][0x2];
	state[0x2][0x2] = t;
	t = state[0x2][0x1];
	state[0x2][0x1] = state[0x2][0x3];
	state[0x2][3] = t;
	
	t = state[0x3][0x0];
	state[0x3][0x0] = state[0x3][0x3];
	state[0x3][0x3] = state[0x3][0x2];
	state[0x3][0x2] = state[0x3][0x1];
	state[0x3][1] = t;
}

void z20(BYTE state[][0x4])
{
	int t;

	t = state[0x1][0x3];
	state[1][0x3] = state[0x1][0x2];
	state[0x1][0x2] = state[1][0x1];
	state[0x1][0x1] = state[1][0x0];
	state[0x1][0x0] = t;
	
	t = state[0x2][0x3];
	state[0x2][0x3] = state[0x2][0x1];
	state[0x2][0x1] = t;
	t = state[0x2][0x2];
	state[0x2][0x2] = state[0x2][0x0];
	state[2][0x0] = t;
	
	t = state[0x3][0x3];
	state[0x3][0x3] = state[0x3][0];
	state[0x3][0x0] = state[0x3][0x1];
	state[0x3][0x1] = state[0x3][0x2];
	state[0x3][0x2] = t;
}

void buf21(BYTE state[][0x4])
{
	BYTE col[4];

	col[0] = state[0x0][0x0];
	col[0x1] = state[0x1][0x0];
	col[0x2] = state[0x2][0x0];
	col[0x3] = state[0x3][0x0];
	state[0x0][0x0] = gf_mul[col[0]][0x0];
	state[0x0][0x0] ^= gf_mul[col[0x1]][0x1];
	state[0][0x0] ^= col[0x2];
	state[0x0][0] ^= col[0x3];
	state[0x1][0x0] = col[0x0];
	state[1][0x0] ^= gf_mul[col[0x1]][0];
	state[0x1][0x0] ^= gf_mul[col[0x2]][1];
	state[0x1][0] ^= col[0x3];
	state[0x2][0x0] = col[0x0];
	state[0x2][0x0] ^= col[0x1];
	state[2][0x0] ^= gf_mul[col[0x2]][0x0];
	state[0x2][0x0] ^= gf_mul[col[0x3]][1];
	state[0x3][0x0] = gf_mul[col[0x0]][0x1];
	state[0x3][0x0] ^= col[0x1];
	state[3][0x0] ^= col[0x2];
	state[0x3][0x0] ^= gf_mul[col[3]][0x0];
	
	col[0x0] = state[0x0][1];
	col[1] = state[0x1][1];
	col[2] = state[0x2][0x1];
	col[0x3] = state[0x3][1];
	state[0x0][1] = gf_mul[col[0x0]][0x0];
	state[0x0][1] ^= gf_mul[col[1]][0x1];
	state[0x0][0x1] ^= col[0x2];
	state[0][0x1] ^= col[3];
	state[1][0x1] = col[0x0];
	state[0x1][0x1] ^= gf_mul[col[0x1]][0x0];
	state[1][1] ^= gf_mul[col[0x2]][0x1];
	state[0x1][0x1] ^= col[0x3];
	state[0x2][0x1] = col[0x0];
	state[0x2][0x1] ^= col[0x1];
	state[0x2][1] ^= gf_mul[col[0x2]][0x0];
	state[2][0x1] ^= gf_mul[col[0x3]][0x1];
	state[3][0x1] = gf_mul[col[0x0]][0x1];
	state[0x3][0x1] ^= col[0x1];
	state[0x3][1] ^= col[0x2];
	state[0x3][0x1] ^= gf_mul[col[0x3]][0x0];
	
	col[0x0] = state[0x0][0x2];
	col[0x1] = state[0x1][0x2];
	col[2] = state[0x2][0x2];
	col[0x3] = state[0x3][0x2];
	state[0x0][0x2] = gf_mul[col[0x0]][0x0];
	state[0x0][2] ^= gf_mul[col[1]][0x1];
	state[0x0][0x2] ^= col[0x2];
	state[0x0][0x2] ^= col[0x3];
	state[0x1][0x2] = col[0x0];
	state[0x1][0x2] ^= gf_mul[col[0x1]][0x0];
	state[0x1][0x2] ^= gf_mul[col[0x2]][0x1];
	state[0x1][0x2] ^= col[0x3];
	state[0x2][0x2] = col[0];
	state[0x2][0x2] ^= col[0x1];
	state[0x2][0x2] ^= gf_mul[col[0x2]][0x0];
	state[0x2][0x2] ^= gf_mul[col[0x3]][0x1];
	state[0x3][0x2] = gf_mul[col[0]][0x1];
	state[0x3][0x2] ^= col[0x1];
	state[0x3][0x2] ^= col[0x2];
	state[0x3][2] ^= gf_mul[col[3]][0x0];
	
	col[0x0] = state[0][0x3];
	col[0x1] = state[0x1][0x3];
	col[0x2] = state[0x2][0x3];
	col[0x3] = state[0x3][0x3];
	state[0x0][0x3] = gf_mul[col[0x0]][0x0];
	state[0x0][0x3] ^= gf_mul[col[0x1]][0x1];
	state[0][0x3] ^= col[0x2];
	state[0x0][0x3] ^= col[0x3];
	state[0x1][0x3] = col[0x0];
	state[0x1][0x3] ^= gf_mul[col[0x1]][0x0];
	state[1][0x3] ^= gf_mul[col[0x2]][0x1];
	state[0x1][0x3] ^= col[0x3];
	state[0x2][0x3] = col[0x0];
	state[0x2][0x3] ^= col[0x1];
	state[0x2][3] ^= gf_mul[col[2]][0];
	state[0x2][0x3] ^= gf_mul[col[0x3]][0x1];
	state[3][0x3] = gf_mul[col[0x0]][0x1];
	state[0x3][3] ^= col[0x1];
	state[0x3][0x3] ^= col[2];
	state[3][0x3] ^= gf_mul[col[3]][0x0];
}

void h022(BYTE state[][0x4])
{
	BYTE col[0x4];

	col[0x0] = state[0x0][0x0];
	col[1] = state[1][0x0];
	col[2] = state[0x2][0x0];
	col[3] = state[3][0x0];
	state[0][0x0] = gf_mul[col[0]][0x5];
	state[0x0][0x0] ^= gf_mul[col[0x1]][0x3];
	state[0x0][0] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x0] ^= gf_mul[col[0x3]][2];
	state[0x1][0x0] = gf_mul[col[0x0]][0x2];
	state[0x1][0] ^= gf_mul[col[0x1]][0x5];
	state[0x1][0x0] ^= gf_mul[col[0x2]][0x3];
	state[1][0] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x0] = gf_mul[col[0x0]][0x4];
	state[0x2][0] ^= gf_mul[col[0x1]][0x2];
	state[2][0x0] ^= gf_mul[col[2]][5];
	state[0x2][0x0] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x0] = gf_mul[col[0]][0x3];
	state[0x3][0x0] ^= gf_mul[col[0x1]][0x4];
	state[0x3][0x0] ^= gf_mul[col[0x2]][0x2];
	state[0x3][0x0] ^= gf_mul[col[0x3]][0x5];
	
	col[0x0] = state[0x0][0x1];
	col[0x1] = state[0x1][1];
	col[0x2] = state[0x2][0x1];
	col[0x3] = state[0x3][0x1];
	state[0x0][0x1] = gf_mul[col[0x0]][0x5];
	state[0x0][0x1] ^= gf_mul[col[1]][3];
	state[0x0][0x1] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x1] ^= gf_mul[col[3]][0x2];
	state[0x1][0x1] = gf_mul[col[0]][0x2];
	state[1][0x1] ^= gf_mul[col[0x1]][0x5];
	state[0x1][1] ^= gf_mul[col[0x2]][0x3];
	state[1][0x1] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x1] = gf_mul[col[0x0]][0x4];
	state[0x2][0x1] ^= gf_mul[col[0x1]][0x2];
	state[2][1] ^= gf_mul[col[0x2]][0x5];
	state[0x2][0x1] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x1] = gf_mul[col[0x0]][0x3];
	state[0x3][1] ^= gf_mul[col[1]][0x4];
	state[0x3][0x1] ^= gf_mul[col[0x2]][0x2];
	state[0x3][0x1] ^= gf_mul[col[3]][0x5];
	
	col[0x0] = state[0x0][0x2];
	col[0x1] = state[1][2];
	col[2] = state[0x2][0x2];
	col[0x3] = state[0x3][0x2];
	state[0x0][0x2] = gf_mul[col[0x0]][0x5];
	state[0x0][0x2] ^= gf_mul[col[0x1]][0x3];
	state[0x0][0x2] ^= gf_mul[col[0x2]][4];
	state[0x0][0x2] ^= gf_mul[col[0x3]][0x2];
	state[0x1][2] = gf_mul[col[0x0]][0x2];
	state[1][0x2] ^= gf_mul[col[0x1]][0x5];
	state[0x1][0x2] ^= gf_mul[col[0x2]][0x3];
	state[0x1][0x2] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x2] = gf_mul[col[0x0]][0x4];
	state[2][0x2] ^= gf_mul[col[1]][0x2];
	state[0x2][0x2] ^= gf_mul[col[0x2]][0x5];
	state[0x2][2] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x2] = gf_mul[col[0x0]][3];
	state[0x3][2] ^= gf_mul[col[0x1]][0x4];
	state[3][0x2] ^= gf_mul[col[2]][0x2];
	state[0x3][0x2] ^= gf_mul[col[3]][0x5];
	
	col[0x0] = state[0x0][0x3];
	col[0x1] = state[0x1][0x3];
	col[0x2] = state[0x2][0x3];
	col[0x3] = state[3][0x3];
	state[0][0x3] = gf_mul[col[0x0]][5];
	state[0x0][0x3] ^= gf_mul[col[0x1]][0x3];
	state[0][0x3] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x3] ^= gf_mul[col[0x3]][0x2];
	state[0x1][3] = gf_mul[col[0x0]][0x2];
	state[0x1][0x3] ^= gf_mul[col[0x1]][0x5];
	state[0x1][0x3] ^= gf_mul[col[2]][0x3];
	state[0x1][0x3] ^= gf_mul[col[0x3]][0x4];
	state[2][0x3] = gf_mul[col[0x0]][0x4];
	state[0x2][0x3] ^= gf_mul[col[0x1]][2];
	state[0x2][0x3] ^= gf_mul[col[2]][0x5];
	state[0x2][0x3] ^= gf_mul[col[3]][0x3];
	state[0x3][0x3] = gf_mul[col[0x0]][0x3];
	state[0x3][3] ^= gf_mul[col[0x1]][0x4];
	state[3][0x3] ^= gf_mul[col[0x2]][0x2];
	state[0x3][0x3] ^= gf_mul[col[0x3]][0x5];
}

void st23(const BYTE in[], BYTE out[], const WORD key[], int keysize)
{
	BYTE state[4][4];

	

	
	state[0x0][0x0] = in[0x0];
	state[0x1][0] = in[0x1];
	state[0x2][0x0] = in[0x2];
	state[0x3][0x0] = in[0x3];
	state[0x0][0x1] = in[0x4];
	state[0x1][0x1] = in[5];
	state[0x2][1] = in[0x6];
	state[0x3][1] = in[0x7];
	state[0x0][0x2] = in[0x8];
	state[0x1][0x2] = in[0x9];
	state[2][2] = in[0xa];
	state[0x3][0x2] = in[0xb];
	state[0][0x3] = in[0xc];
	state[1][0x3] = in[0xd];
	state[2][0x3] = in[0xe];
	state[0x3][0x3] = in[0xf];

	
	acc16(state,&key[0x0]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0x4]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[8]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0xc]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0x10]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[20]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[24]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0x1c]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0x20]);
	kx17(state); v19(state); buf21(state); acc16(state,&key[0x24]);
	if (keysize != 0x80) {
		kx17(state); v19(state); buf21(state); acc16(state,&key[0x28]);
		kx17(state); v19(state); buf21(state); acc16(state,&key[0x2c]);
		if (keysize != 0xc0) {
			kx17(state); v19(state); buf21(state); acc16(state,&key[0x30]);
			kx17(state); v19(state); buf21(state); acc16(state,&key[0x34]);
			kx17(state); v19(state); acc16(state,&key[0x38]);
		}
		else {
			kx17(state); v19(state); acc16(state,&key[0x30]);
		}
	}
	else {
		kx17(state); v19(state); acc16(state,&key[0x28]);
	}

	out[0x0] = state[0x0][0x0];
	out[0x1] = state[0x1][0];
	out[0x2] = state[0x2][0x0];
	out[0x3] = state[0x3][0x0];
	out[0x4] = state[0x0][0x1];
	out[0x5] = state[0x1][0x1];
	out[6] = state[0x2][0x1];
	out[0x7] = state[0x3][1];
	out[0x8] = state[0x0][0x2];
	out[0x9] = state[0x1][0x2];
	out[10] = state[0x2][0x2];
	out[0xb] = state[0x3][0x2];
	out[0xc] = state[0x0][0x3];
	out[0xd] = state[0x1][0x3];
	out[0xe] = state[0x2][0x3];
	out[0xf] = state[0x3][3];
}

void x24(const BYTE in[], BYTE out[], const WORD key[], int keysize)
{
	BYTE state[4][0x4];

	state[0][0x0] = in[0x0];
	state[0x1][0x0] = in[0x1];
	state[0x2][0x0] = in[0x2];
	state[3][0x0] = in[0x3];
	state[0][1] = in[0x4];
	state[0x1][1] = in[0x5];
	state[0x2][0x1] = in[6];
	state[0x3][0x1] = in[0x7];
	state[0x0][2] = in[0x8];
	state[0x1][0x2] = in[0x9];
	state[0x2][0x2] = in[0xa];
	state[0x3][0x2] = in[0xb];
	state[0x0][0x3] = in[0xc];
	state[0x1][3] = in[0xd];
	state[2][0x3] = in[0xe];
	state[0x3][0x3] = in[0xf];

	
	if (keysize > 0x80) {
		if (keysize > 0xc0) {
			acc16(state,&key[0x38]);
			z20(state);rnd18(state);acc16(state,&key[0x34]);h022(state);
			z20(state);rnd18(state);acc16(state,&key[0x30]);h022(state);
		}
		else {
			acc16(state,&key[0x30]);
		}
		z20(state);rnd18(state);acc16(state,&key[0x2c]);h022(state);
		z20(state);rnd18(state);acc16(state,&key[0x28]);h022(state);
	}
	else {
		acc16(state,&key[40]);
	}
	z20(state);rnd18(state);acc16(state,&key[0x24]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[32]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x1c]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x18]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x14]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x10]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0xc]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x8]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0x4]);h022(state);
	z20(state);rnd18(state);acc16(state,&key[0]);

	out[0] = state[0x0][0x0];
	out[1] = state[0x1][0x0];
	out[0x2] = state[2][0x0];
	out[3] = state[0x3][0x0];
	out[0x4] = state[0x0][0x1];
	out[0x5] = state[0x1][0x1];
	out[6] = state[2][0x1];
	out[7] = state[0x3][0x1];
	out[0x8] = state[0x0][0x2];
	out[0x9] = state[0x1][0x2];
	out[10] = state[0x2][2];
	out[0xb] = state[0x3][0x2];
	out[0xc] = state[0x0][0x3];
	out[13] = state[0x1][0x3];
	out[0xe] = state[0x2][0x3];
	out[15] = state[0x3][0x3];
}

