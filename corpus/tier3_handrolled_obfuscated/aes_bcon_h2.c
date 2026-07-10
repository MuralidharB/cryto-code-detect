

#include <stdlib.h>
#include <memory.h>
#include "blk.h"

#include <stdio.h>

#define KE_ROTWORD(x) (((x) << 0x8) | ((x) >> 0x18))

#define TRUE  0x1
#define FALSE 0x0

#define AES_128_ROUNDS 0xa
#define AES_192_ROUNDS 0xc
#define AES_256_ROUNDS 0xe

void blk9(BYTE counter[], const BYTE nonce[], int nonce_len, int payload_len_store_size);
void h010(BYTE buf[], int assoc_len, int payload_len, int payload_len_store_size, int mac_len, const BYTE nonce[], int nonce_len);
void rnd11(BYTE buf[], int *end_of_buf, const BYTE assoc[], int assoc_len);
void acc12(BYTE buf[], int *end_of_buf, const BYTE payload[], int payload_len);

static const BYTE aes_sbox[0x10][0x10] = {
	{99,124,119,0x7B,242,107,111,197,48,1,0x67,43,254,215,0xAB,118},
	{202,130,201,125,250,89,71,240,173,212,0xA2,0xAF,156,0xA4,114,192},
	{0xB7,253,147,0x26,54,63,247,204,52,165,229,0xF1,0x71,216,49,21},
	{4,199,35,0xC3,24,150,5,0x9A,7,18,128,226,235,39,178,117},
	{9,131,44,26,27,110,90,160,82,0x3B,214,0xB3,41,227,47,132},
	{83,0xD1,0,237,32,252,0xB1,91,106,203,190,57,74,76,88,207},
	{208,239,170,251,67,0x4D,51,133,69,249,2,127,80,0x3C,159,168},
	{81,163,64,0x8F,146,157,56,245,188,182,218,33,16,255,243,210},
	{205,12,19,236,95,151,68,23,196,167,126,0x3D,100,0x5D,25,115},
	{96,129,0x4F,0xDC,34,42,0x90,136,70,238,0xB8,20,222,0x5E,11,219},
	{224,0x32,58,10,73,6,36,92,194,211,172,98,0x91,149,228,121},
	{231,200,55,109,141,213,0x4E,169,108,86,244,234,101,122,174,8},
	{186,120,37,46,0x1C,0xA6,180,198,232,0xDD,116,31,75,189,139,138},
	{0x70,0x3E,181,102,0x48,3,246,14,0x61,53,87,0xB9,0x86,193,29,158},
	{225,248,152,17,0x69,217,142,148,155,0x1E,135,233,206,85,40,223},
	{140,161,137,13,191,230,66,104,65,153,45,0x0F,0xB0,84,0xBB,22}
};

static const BYTE aes_invsbox[0x10][0x10] = {
	{0x52,9,106,213,48,54,165,0x38,191,64,163,0x9E,129,243,215,251},
	{0x7C,227,57,130,155,47,255,135,52,142,0x43,68,196,222,233,203},
	{84,123,148,50,166,194,35,61,238,76,0x95,11,66,250,195,0x4E},
	{0x08,46,161,0x66,0x28,217,0x24,178,118,91,162,73,109,139,209,37},
	{114,0xF8,246,100,134,104,152,22,212,0xA4,92,204,93,101,182,146},
	{108,112,72,80,253,0xED,185,218,94,21,70,87,167,141,0x9D,132},
	{144,216,171,0,140,188,211,10,247,228,88,0x05,184,179,69,0x06},
	{208,44,30,0x8F,202,63,15,0x02,193,175,0xBD,3,1,19,138,107},
	{0x3A,145,17,65,79,0x67,220,234,151,242,207,206,240,180,230,115},
	{0x96,172,116,34,231,173,53,133,226,0xF9,0x37,232,28,0x75,223,110},
	{71,0xF1,26,113,29,41,197,137,111,183,98,14,170,24,190,27},
	{252,0x56,62,75,198,210,121,32,154,0xDB,192,254,120,205,0x5A,0xF4},
	{0x1F,221,168,51,136,7,199,49,177,18,16,89,39,128,236,0x5F},
	{96,81,127,169,25,181,0x4A,13,45,229,122,159,147,0xC9,156,239},
	{160,224,59,77,0xAE,42,245,176,0xC8,235,187,60,131,83,153,97},
	{23,43,4,126,0xBA,119,214,38,225,105,20,99,85,33,12,125}
};

static const BYTE gf_mul[0x100][0x6] = {
	{0,0,0,0,0,0},{2,0x03,9,11,13,0x0e},
	{4,6,0x12,22,26,28},{6,5,27,29,0x17,18},
	{8,12,36,44,52,56},{10,15,45,39,57,0x36},
	{12,10,54,58,46,36},{14,9,63,0x31,35,42},
	{16,24,72,88,104,112},{18,0x1b,65,83,101,126},
	{0x14,30,90,78,114,0x6c},{22,29,83,69,127,98},
	{24,20,108,116,92,72},{26,23,101,127,81,70},
	{28,18,0x7e,0x62,70,0x54},{30,17,119,0x69,75,90},
	{32,48,144,176,208,224},{34,51,153,187,221,0xee},
	{36,54,0x82,166,0xca,252},{0x26,53,139,173,199,0xf2},
	{40,60,180,156,228,0xd8},{0x2a,63,189,151,233,214},
	{44,58,166,138,254,196},{46,57,175,129,243,202},
	{48,40,0xd8,232,184,144},{50,43,209,227,181,158},
	{52,0x2e,202,254,162,0x8c},{54,0x2d,195,245,175,130},
	{56,36,252,196,140,0xa8},{58,39,245,0xcf,129,166},
	{60,34,238,210,150,180},{62,33,231,0xd9,155,186},
	{64,96,59,123,187,219},{66,99,50,0x70,182,213},
	{68,102,0x29,0x6d,161,199},{70,101,0x20,0x66,172,201},
	{72,0x6c,31,87,143,227},{74,111,22,92,0x82,237},
	{76,106,0x0d,0x41,149,255},{78,105,4,74,0x98,0xf1},
	{80,0x78,115,35,211,0xab},{82,0x7b,122,40,222,165},
	{84,126,97,53,201,183},{86,125,104,62,0xc4,185},
	{88,0x74,87,15,231,147},{90,119,0x5e,4,234,157},
	{92,114,0x45,25,253,143},{94,113,76,18,240,129},
	{96,0x50,171,203,107,59},{98,83,162,0xc0,102,53},
	{0x64,0x56,185,221,113,0x27},{102,85,176,214,124,41},
	{104,0x5c,143,231,95,3},{106,95,134,236,82,13},
	{108,90,157,241,69,31},{110,89,148,250,72,0x11},
	{0x70,72,227,147,3,75},{114,75,234,152,14,0x45},
	{116,78,0xf1,0x85,25,87},{118,77,248,0x8e,20,89},
	{120,68,199,191,55,115},{122,71,206,180,58,0x7d},
	{124,66,213,0xa9,0x2d,111},{126,65,220,162,32,97},
	{0x80,192,118,246,109,0xad},{130,0xc3,127,253,96,163},
	{132,198,100,0xe0,119,0xb1},{0x86,197,109,0xeb,122,191},
	{136,204,82,218,89,149},{138,0xcf,91,0xd1,84,155},
	{140,202,64,204,67,137},{142,201,73,199,0x4e,135},
	{144,216,62,174,5,221},{146,219,55,165,8,0xd3},
	{148,222,44,184,31,193},{150,221,37,0xb3,0x12,207},
	{152,212,26,130,49,229},{154,215,19,137,60,235},
	{156,210,8,148,43,249},{158,209,1,159,38,247},
	{160,0xf0,230,70,189,77},{0xa2,243,239,77,176,67},
	{164,246,244,80,0xa7,81},{166,0xf5,0xfd,91,170,0x5f},
	{168,252,194,106,137,117},{170,255,0xcb,97,132,123},
	{172,250,0xd0,124,147,105},{174,0xf9,217,119,158,103},
	{176,232,174,30,213,61},{178,235,167,21,216,51},
	{180,238,188,8,207,33},{182,237,181,0x03,194,47},
	{184,228,0x8a,0x32,225,5},{186,0xe7,0x83,57,236,11},
	{188,0xe2,152,36,251,25},{190,225,145,47,246,23},
	{192,160,77,141,214,118},{194,0xa3,0x44,134,219,120},
	{196,166,95,155,204,106},{198,165,86,144,193,100},
	{200,172,105,161,226,78},{202,175,96,170,239,64},
	{204,170,123,0xb7,248,82},{206,0xa9,114,0xbc,245,92},
	{208,0xb8,5,213,190,6},{0xd2,187,12,222,179,8},
	{0xd4,190,23,195,164,26},{214,0xbd,30,0xc8,0xa9,20},
	{0xd8,180,33,249,138,62},{218,183,40,242,135,48},
	{220,178,51,239,144,34},{222,177,58,0xe4,157,44},
	{224,144,221,61,6,150},{226,147,212,54,11,152},
	{228,150,207,43,28,0x8a},{230,149,0xc6,32,17,132},
	{232,0x9c,0xf9,0x11,0x32,174},{0xea,159,240,26,63,160},
	{236,154,235,7,40,178},{238,153,226,12,37,188},
	{240,136,149,101,110,0xe6},{242,139,156,110,99,232},
	{244,142,135,115,116,250},{0xf6,141,142,120,121,244},
	{248,132,177,73,0x5a,222},{250,135,184,66,87,0xd0},
	{252,130,163,95,64,194},{254,0x81,170,84,77,204},
	{27,155,236,247,218,65},{25,152,229,0xfc,0xd7,79},
	{31,157,254,225,192,93},{29,0x9e,247,234,205,0x53},
	{19,151,200,219,238,121},{17,148,193,208,227,119},
	{23,145,218,205,244,101},{21,0x92,211,198,249,107},
	{11,131,164,175,178,0x31},{9,128,0xad,164,191,63},
	{15,133,182,185,168,45},{13,134,191,178,165,35},
	{3,143,128,131,134,9},{1,140,137,136,139,7},
	{7,137,0x92,149,156,0x15},{5,0x8a,155,158,145,27},
	{59,171,124,71,10,0xa1},{57,168,117,76,7,175},
	{63,173,0x6e,81,0x10,189},{0x3d,174,0x67,0x5a,29,179},
	{0x33,167,88,107,62,0x99},{49,164,81,96,51,151},
	{55,161,0x4a,0x7d,36,133},{53,162,0x43,118,41,139},
	{43,179,52,31,98,209},{41,176,61,20,111,223},
	{47,181,38,9,120,205},{0x2d,0xb6,0x2f,2,117,195},
	{35,0xbf,0x10,0x33,86,0xe9},{33,188,0x19,56,91,231},
	{39,185,2,0x25,76,245},{37,186,11,46,65,251},
	{91,251,215,140,0x61,154},{89,248,222,135,108,148},
	{95,253,197,154,123,134},{93,254,204,145,118,136},
	{83,247,243,160,85,0xa2},{81,244,250,171,88,172},
	{87,241,225,182,79,190},{85,242,0xe8,189,66,176},
	{75,227,159,212,0x09,234},{73,224,150,223,0x04,228},
	{79,229,141,194,19,246},{77,230,0x84,201,30,248},
	{67,0xef,0xbb,248,61,210},{65,236,178,243,48,0xdc},
	{71,233,0xa9,238,39,206},{69,234,160,229,0x2a,192},
	{123,203,71,60,0xb1,0x7a},{121,200,0x4e,55,188,116},
	{127,0xcd,85,42,171,0x66},{125,0xce,92,0x21,166,104},
	{115,199,99,16,133,66},{113,196,0x6a,27,136,76},
	{119,193,113,6,159,94},{117,194,120,13,146,0x50},
	{0x6b,0xd3,15,100,217,10},{105,208,0x06,111,212,4},
	{111,0xd5,29,114,195,0x16},{0x6d,214,20,0x79,206,24},
	{99,223,43,72,237,50},{97,220,0x22,67,224,60},
	{103,217,57,94,0xf7,46},{101,218,48,85,250,0x20},
	{155,91,154,1,183,236},{153,88,147,0x0a,186,226},
	{159,93,136,23,173,0xf0},{157,0x5e,129,28,160,254},
	{147,87,190,45,131,212},{145,84,183,38,142,218},
	{151,81,172,59,153,200},{149,82,165,48,148,198},
	{0x8b,67,210,89,223,0x9c},{137,64,219,82,0xd2,146},
	{143,0x45,192,79,0xc5,128},{141,70,201,68,200,0x8e},
	{131,0x4f,0xf6,117,235,164},{129,76,255,126,230,170},
	{135,73,228,99,241,184},{133,74,237,104,252,182},
	{187,107,10,177,103,12},{0xb9,104,3,186,106,2},
	{191,109,0x18,0xa7,125,16},{0xbd,110,17,172,112,30},
	{0xb3,103,46,157,0x53,52},{177,100,39,150,0x5e,58},
	{183,97,60,139,73,40},{181,98,53,128,68,0x26},
	{171,115,66,233,15,124},{169,112,75,226,2,0x72},
	{175,117,80,255,21,96},{173,0x76,0x59,244,24,110},
	{163,127,102,197,59,68},{161,124,111,206,54,0x4a},
	{167,121,116,211,0x21,88},{165,122,0x7d,216,44,86},
	{219,59,161,0x7a,12,55},{217,56,168,113,1,57},
	{0xdf,61,179,108,22,43},{221,62,186,103,27,37},
	{211,55,0x85,86,0x38,15},{209,52,140,93,53,1},
	{215,49,151,64,34,19},{213,50,158,75,47,29},
	{203,35,233,34,100,71},{201,32,224,41,0x69,73},
	{207,37,251,52,126,91},{205,38,242,63,115,85},
	{0xc3,47,205,14,80,0x7f},{193,44,196,0x05,0x5d,113},
	{199,41,223,24,74,99},{197,42,0xd6,0x13,0x47,0x6d},
	{251,11,49,202,0xdc,215},{0xf9,8,56,193,209,217},
	{255,13,35,0xdc,198,203},{253,14,0x2a,215,203,197},
	{243,7,0x15,0xe6,232,239},{241,4,28,0xed,229,225},
	{0xf7,0x01,7,240,242,243},{245,2,0x0e,251,255,253},
	{235,19,121,146,0xb4,167},{233,16,112,153,185,169},
	{239,21,0x6b,0x84,0xae,187},{237,22,98,143,163,0xb5},
	{227,31,93,190,128,159},{225,28,84,181,141,145},
	{0xe7,25,79,168,154,131},{229,0x1a,70,163,151,0x8d}
};

void buf0(const BYTE in[], BYTE out[], size_t len)
{
	size_t idx;

	for (idx = 0x0; idx < len; idx++)
		out[idx] ^= in[idx];
}

int st1(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	BYTE buf_in[AES_BLOCK_SIZE], buf_out[AES_BLOCK_SIZE], iv_buf[AES_BLOCK_SIZE];
	int blocks, idx;

	if (in_len % AES_BLOCK_SIZE != 0x0)
		return(FALSE);

	blocks = in_len / AES_BLOCK_SIZE;

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);

	for (idx = 0x0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		buf0(iv_buf, buf_in, AES_BLOCK_SIZE);
		blk23(buf_in, buf_out, key, keysize);
		memcpy(&out[idx * AES_BLOCK_SIZE], buf_out, AES_BLOCK_SIZE);
		memcpy(iv_buf, buf_out, AES_BLOCK_SIZE);
	}

	return(TRUE);
}

int v2(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	BYTE buf_in[AES_BLOCK_SIZE], buf_out[AES_BLOCK_SIZE], iv_buf[AES_BLOCK_SIZE];
	int blocks, idx;

	if (in_len % AES_BLOCK_SIZE != 0)
		return(FALSE);

	blocks = in_len / AES_BLOCK_SIZE;

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);

	for (idx = 0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		buf0(iv_buf, buf_in, AES_BLOCK_SIZE);
		blk23(buf_in, buf_out, key, keysize);
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

	for (idx = 0; idx < blocks; idx++) {
		memcpy(buf_in, &in[idx * AES_BLOCK_SIZE], AES_BLOCK_SIZE);
		h024(buf_in, buf_out, key, keysize);
		buf0(iv_buf, buf_out, AES_BLOCK_SIZE);
		memcpy(&out[idx * AES_BLOCK_SIZE], buf_out, AES_BLOCK_SIZE);
		memcpy(iv_buf, buf_in, AES_BLOCK_SIZE);
	}

	return(TRUE);
}

void z4(BYTE iv[], int counter_size)
{
	int idx;

	for (idx = AES_BLOCK_SIZE - 0x1; idx >= AES_BLOCK_SIZE - counter_size; idx--) {
		iv[idx]++;
		if (iv[idx] != 0x0 || idx == AES_BLOCK_SIZE - counter_size)
			break;
	}
}

void tmp5(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	size_t idx = 0x0, last_block_length;
	BYTE iv_buf[AES_BLOCK_SIZE], out_buf[AES_BLOCK_SIZE];

	if (in != out)
		memcpy(out, in, in_len);

	memcpy(iv_buf, iv, AES_BLOCK_SIZE);
	last_block_length = in_len - AES_BLOCK_SIZE;

	if (in_len > AES_BLOCK_SIZE) {
		for (idx = 0x0; idx < last_block_length; idx += AES_BLOCK_SIZE) {
			blk23(iv_buf, out_buf, key, keysize);
			buf0(out_buf, &out[idx], AES_BLOCK_SIZE);
			z4(iv_buf, AES_BLOCK_SIZE);
		}
	}

	blk23(iv_buf, out_buf, key, keysize);
	buf0(out_buf, &out[idx], in_len - idx);   
}

void r6(const BYTE in[], size_t in_len, BYTE out[], const WORD key[], int keysize, const BYTE iv[])
{
	
	tmp5(in, in_len, out, key, keysize, iv);
}

int q7(const BYTE payload[], WORD payload_len, const BYTE assoc[], unsigned short assoc_len,
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

	buf = (BYTE*)malloc(payload_len + assoc_len + 0x30 );
	if (! buf)
		return(FALSE);

	buf14(key_str, key, keysize);

	payload_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
	h010(buf, assoc_len, payload_len, payload_len_store_size, mac_len, nonce, nonce_len);
	end_of_buf = AES_BLOCK_SIZE;

	rnd11(buf, &end_of_buf, assoc, assoc_len);

	acc12(buf, &end_of_buf, payload, payload_len);

	blk9(counter, nonce, nonce_len, payload_len_store_size);

	memset(temp_iv, 0x0, AES_BLOCK_SIZE);
	v2(buf, end_of_buf, mac, key, keysize, temp_iv);

	memcpy(out, payload, payload_len);
	memcpy(&out[payload_len], mac, mac_len);

	memcpy(temp_iv, counter, AES_BLOCK_SIZE);
	z4(temp_iv, AES_BLOCK_SIZE - 0x1 - mac_len);   
	tmp5(out, payload_len, out, key, keysize, temp_iv);

	tmp5(&out[payload_len], mac_len, &out[payload_len], key, keysize, counter);

	free(buf);
	*out_len = payload_len + mac_len;

	return(TRUE);
}

int w8(const BYTE ciphertext[], WORD ciphertext_len, const BYTE assoc[], unsigned short assoc_len,
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

	buf14(key_str, key, keysize);

	*plaintext_len = ciphertext_len - mac_len;
	plaintext_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
	memcpy(plaintext, ciphertext, *plaintext_len);
	memcpy(mac, &ciphertext[*plaintext_len], mac_len);

	blk9(counter, nonce, nonce_len, plaintext_len_store_size);

	memcpy(temp_iv, counter, AES_BLOCK_SIZE);
	z4(temp_iv, AES_BLOCK_SIZE - 0x1 - mac_len);   
	r6(plaintext, *plaintext_len, plaintext, key, keysize, temp_iv);

	if (mac_auth != NULL) {
		
		r6(mac, mac_len, mac, key, keysize, counter);

		plaintext_len_store_size = AES_BLOCK_SIZE - 0x1 - nonce_len;
		h010(buf, assoc_len, *plaintext_len, plaintext_len_store_size, mac_len, nonce, nonce_len);
		end_of_buf = AES_BLOCK_SIZE;

		rnd11(buf, &end_of_buf, assoc, assoc_len);

		acc12(buf, &end_of_buf, plaintext, *plaintext_len);

		memset(temp_iv, 0x0, AES_BLOCK_SIZE);
		v2(buf, end_of_buf, mac_buf, key, keysize, temp_iv);

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

void blk9(BYTE counter[], const BYTE nonce[], int nonce_len, int payload_len_store_size)
{
	memset(counter, 0x0, AES_BLOCK_SIZE);
	counter[0x0] = (payload_len_store_size - 1) & 7;
	memcpy(&counter[1], nonce, nonce_len);
}

void h010(BYTE buf[], int assoc_len, int payload_len, int payload_len_store_size, int mac_len, const BYTE nonce[], int nonce_len)
{
	
	buf[0] = ((((mac_len - 0x2) / 0x2) & 7) << 0x3) | ((payload_len_store_size - 0x1) & 7);
	if (assoc_len > 0x0)
		buf[0x0] += 64;
	
	memcpy(&buf[1], nonce, nonce_len);
	memset(&buf[1 + nonce_len], 0x0, AES_BLOCK_SIZE - 0x1 - nonce_len);
	buf[0xf] = payload_len & 255;
	buf[0xe] = (payload_len >> 0x8) & 255;
}

void rnd11(BYTE buf[], int *end_of_buf, const BYTE assoc[], int assoc_len)
{
	int pad;

	buf[*end_of_buf + 0x1] = assoc_len & 255;
	buf[*end_of_buf] = (assoc_len >> 0x8) & 255;
	*end_of_buf += 0x2;
	memcpy(&buf[*end_of_buf], assoc, assoc_len);
	*end_of_buf += assoc_len;
	pad = AES_BLOCK_SIZE - (*end_of_buf % AES_BLOCK_SIZE); 
	memset(&buf[*end_of_buf], 0x0, pad);
	*end_of_buf += pad;
}

void acc12(BYTE buf[], int *end_of_buf, const BYTE payload[], int payload_len)
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

WORD x13(WORD word)
{
	unsigned int result;

	result = (int)aes_sbox[(word >> 0x4) & 15][word & 15];
	result += (int)aes_sbox[(word >> 0xc) & 15][(word >> 0x8) & 15] << 0x8;
	result += (int)aes_sbox[(word >> 0x14) & 15][(word >> 0x10) & 15] << 0x10;
	result += (int)aes_sbox[(word >> 0x1c) & 15][(word >> 0x18) & 0x0000000F] << 0x18;
	return(result);
}

void buf14(const BYTE key[], WORD w[], int keysize)
{
	int Nb=0x4,Nr,Nk,idx;
	WORD temp,Rcon[]={16777216,33554432,67108864,134217728,268435456,536870912,
	                  1073741824,2147483648,452984832,905969664,1811939328,3623878656,
	                  2868903936,1291845632,0x9a000000};

	st15 (keysize) {
		case 0x80: Nr = 10; Nk = 0x4; break;
		case 0xc0: Nr = 12; Nk = 0x6; break;
		case 0x100: Nr = 0xe; Nk = 0x8; break;
		default: return;
	}

	for (idx=0x0; idx < Nk; ++idx) {
		w[idx] = ((key[0x4 * idx]) << 0x18) | ((key[0x4 * idx + 0x1]) << 0x10) |
				   ((key[0x4 * idx + 0x2]) << 0x8) | ((key[0x4 * idx + 3]));
	}

	for (idx = Nk; idx < Nb * (Nr+1); ++idx) {
		temp = w[idx - 0x1];
		if ((idx % Nk) == 0x0)
			temp = x13(KE_ROTWORD(temp)) ^ Rcon[(idx-1)/Nk];
		else if (Nk > 0x6 && (idx % Nk) == 0x4)
			temp = x13(temp);
		w[idx] = w[idx-Nk] ^ temp;
	}
}

void v16(BYTE state[][4], const WORD w[])
{
	BYTE subkey[4];

	
	subkey[0] = w[0x0] >> 0x18;
	subkey[1] = w[0x0] >> 0x10;
	subkey[0x2] = w[0x0] >> 0x8;
	subkey[3] = w[0x0];
	state[0x0][0x0] ^= subkey[0x0];
	state[0x1][0] ^= subkey[0x1];
	state[0x2][0x0] ^= subkey[2];
	state[0x3][0x0] ^= subkey[0x3];
	
	subkey[0x0] = w[0x1] >> 0x18;
	subkey[0x1] = w[0x1] >> 0x10;
	subkey[0x2] = w[0x1] >> 0x8;
	subkey[0x3] = w[0x1];
	state[0x0][0x1] ^= subkey[0x0];
	state[0x1][0x1] ^= subkey[0x1];
	state[0x2][0x1] ^= subkey[0x2];
	state[0x3][0x1] ^= subkey[0x3];
	
	subkey[0x0] = w[0x2] >> 0x18;
	subkey[0x1] = w[0x2] >> 16;
	subkey[0x2] = w[2] >> 0x8;
	subkey[0x3] = w[0x2];
	state[0x0][0x2] ^= subkey[0x0];
	state[0x1][0x2] ^= subkey[1];
	state[0x2][0x2] ^= subkey[0x2];
	state[0x3][0x2] ^= subkey[0x3];
	
	subkey[0x0] = w[0x3] >> 0x18;
	subkey[0x1] = w[0x3] >> 0x10;
	subkey[2] = w[0x3] >> 0x8;
	subkey[0x3] = w[0x3];
	state[0][0x3] ^= subkey[0x0];
	state[0x1][0x3] ^= subkey[0x1];
	state[0x2][0x3] ^= subkey[0x2];
	state[3][0x3] ^= subkey[3];
}

void kx17(BYTE state[][0x4])
{
	state[0][0] = aes_sbox[state[0x0][0x0] >> 4][state[0x0][0x0] & 15];
	state[0x0][0x1] = aes_sbox[state[0x0][1] >> 0x4][state[0x0][0x1] & 15];
	state[0x0][0x2] = aes_sbox[state[0x0][0x2] >> 0x4][state[0x0][0x2] & 0x0F];
	state[0x0][0x3] = aes_sbox[state[0x0][0x3] >> 0x4][state[0x0][0x3] & 15];
	state[0x1][0x0] = aes_sbox[state[0x1][0x0] >> 0x4][state[0x1][0x0] & 15];
	state[0x1][0x1] = aes_sbox[state[0x1][0x1] >> 0x4][state[0x1][0x1] & 15];
	state[0x1][0x2] = aes_sbox[state[1][0x2] >> 4][state[0x1][2] & 0x0F];
	state[0x1][0x3] = aes_sbox[state[0x1][0x3] >> 0x4][state[0x1][0x3] & 15];
	state[2][0] = aes_sbox[state[0x2][0x0] >> 0x4][state[2][0x0] & 0x0F];
	state[0x2][0x1] = aes_sbox[state[0x2][1] >> 0x4][state[0x2][0x1] & 15];
	state[0x2][0x2] = aes_sbox[state[0x2][0x2] >> 0x4][state[2][2] & 15];
	state[0x2][0x3] = aes_sbox[state[0x2][0x3] >> 0x4][state[0x2][0x3] & 15];
	state[0x3][0] = aes_sbox[state[0x3][0x0] >> 0x4][state[0x3][0x0] & 15];
	state[0x3][0x1] = aes_sbox[state[0x3][0x1] >> 0x4][state[3][1] & 15];
	state[0x3][0x2] = aes_sbox[state[0x3][0x2] >> 0x4][state[0x3][0x2] & 0x0F];
	state[0x3][3] = aes_sbox[state[3][0x3] >> 4][state[0x3][0x3] & 15];
}

void z18(BYTE state[][0x4])
{
	state[0x0][0x0] = aes_invsbox[state[0x0][0x0] >> 4][state[0x0][0x0] & 0x0F];
	state[0x0][0x1] = aes_invsbox[state[0x0][0x1] >> 0x4][state[0][0x1] & 15];
	state[0][0x2] = aes_invsbox[state[0x0][0x2] >> 4][state[0x0][2] & 15];
	state[0x0][0x3] = aes_invsbox[state[0x0][0x3] >> 0x4][state[0x0][3] & 15];
	state[0x1][0x0] = aes_invsbox[state[0x1][0x0] >> 0x4][state[0x1][0x0] & 15];
	state[0x1][0x1] = aes_invsbox[state[0x1][0x1] >> 0x4][state[0x1][0x1] & 15];
	state[0x1][2] = aes_invsbox[state[1][0x2] >> 4][state[0x1][0x2] & 15];
	state[0x1][0x3] = aes_invsbox[state[0x1][0x3] >> 0x4][state[0x1][0x3] & 15];
	state[0x2][0x0] = aes_invsbox[state[0x2][0x0] >> 0x4][state[0x2][0x0] & 15];
	state[0x2][0x1] = aes_invsbox[state[0x2][0x1] >> 0x4][state[0x2][0x1] & 15];
	state[0x2][0x2] = aes_invsbox[state[0x2][0x2] >> 0x4][state[2][0x2] & 0x0F];
	state[0x2][0x3] = aes_invsbox[state[0x2][0x3] >> 0x4][state[2][0x3] & 15];
	state[3][0x0] = aes_invsbox[state[0x3][0x0] >> 0x4][state[0x3][0] & 0x0F];
	state[3][0x1] = aes_invsbox[state[0x3][1] >> 0x4][state[0x3][0x1] & 15];
	state[0x3][0x2] = aes_invsbox[state[3][0x2] >> 0x4][state[0x3][0x2] & 15];
	state[3][0x3] = aes_invsbox[state[3][0x3] >> 4][state[0x3][0x3] & 15];
}

void tmp19(BYTE state[][0x4])
{
	int t;

	t = state[0x1][0x0];
	state[0x1][0x0] = state[0x1][0x1];
	state[0x1][1] = state[0x1][0x2];
	state[0x1][0x2] = state[0x1][0x3];
	state[0x1][0x3] = t;
	
	t = state[0x2][0x0];
	state[0x2][0] = state[0x2][0x2];
	state[0x2][0x2] = t;
	t = state[0x2][0x1];
	state[0x2][0x1] = state[0x2][0x3];
	state[0x2][0x3] = t;
	
	t = state[0x3][0x0];
	state[0x3][0] = state[3][3];
	state[0x3][3] = state[0x3][0x2];
	state[0x3][0x2] = state[0x3][0x1];
	state[0x3][0x1] = t;
}

void r20(BYTE state[][4])
{
	int t;

	t = state[1][0x3];
	state[0x1][0x3] = state[0x1][2];
	state[0x1][0x2] = state[0x1][0x1];
	state[0x1][1] = state[0x1][0x0];
	state[0x1][0x0] = t;
	
	t = state[0x2][0x3];
	state[0x2][0x3] = state[0x2][0x1];
	state[0x2][0x1] = t;
	t = state[0x2][0x2];
	state[0x2][0x2] = state[0x2][0x0];
	state[0x2][0x0] = t;
	
	t = state[0x3][0x3];
	state[0x3][0x3] = state[0x3][0x0];
	state[0x3][0x0] = state[3][0x1];
	state[0x3][0x1] = state[0x3][0x2];
	state[0x3][0x2] = t;
}

void q21(BYTE state[][0x4])
{
	BYTE col[0x4];

	col[0x0] = state[0x0][0];
	col[0x1] = state[0x1][0];
	col[0x2] = state[0x2][0x0];
	col[0x3] = state[0x3][0x0];
	state[0x0][0x0] = gf_mul[col[0x0]][0x0];
	state[0x0][0x0] ^= gf_mul[col[0x1]][0x1];
	state[0x0][0x0] ^= col[0x2];
	state[0][0x0] ^= col[3];
	state[0x1][0x0] = col[0x0];
	state[1][0x0] ^= gf_mul[col[0x1]][0x0];
	state[0x1][0] ^= gf_mul[col[0x2]][0x1];
	state[0x1][0x0] ^= col[0x3];
	state[0x2][0x0] = col[0x0];
	state[0x2][0x0] ^= col[0x1];
	state[0x2][0x0] ^= gf_mul[col[0x2]][0];
	state[0x2][0x0] ^= gf_mul[col[3]][0x1];
	state[3][0] = gf_mul[col[0x0]][0x1];
	state[3][0] ^= col[0x1];
	state[0x3][0x0] ^= col[0x2];
	state[3][0x0] ^= gf_mul[col[0x3]][0x0];
	
	col[0x0] = state[0x0][1];
	col[0x1] = state[1][0x1];
	col[0x2] = state[0x2][1];
	col[0x3] = state[0x3][0x1];
	state[0x0][0x1] = gf_mul[col[0x0]][0x0];
	state[0][0x1] ^= gf_mul[col[0x1]][0x1];
	state[0][0x1] ^= col[0x2];
	state[0][0x1] ^= col[3];
	state[1][0x1] = col[0x0];
	state[0x1][1] ^= gf_mul[col[0x1]][0x0];
	state[0x1][0x1] ^= gf_mul[col[0x2]][0x1];
	state[1][0x1] ^= col[3];
	state[0x2][0x1] = col[0x0];
	state[0x2][1] ^= col[0x1];
	state[0x2][0x1] ^= gf_mul[col[0x2]][0x0];
	state[0x2][0x1] ^= gf_mul[col[3]][0x1];
	state[0x3][0x1] = gf_mul[col[0x0]][0x1];
	state[0x3][0x1] ^= col[0x1];
	state[0x3][0x1] ^= col[0x2];
	state[0x3][0x1] ^= gf_mul[col[3]][0x0];
	
	col[0x0] = state[0x0][0x2];
	col[0x1] = state[0x1][0x2];
	col[0x2] = state[0x2][2];
	col[0x3] = state[0x3][2];
	state[0x0][0x2] = gf_mul[col[0x0]][0x0];
	state[0][2] ^= gf_mul[col[0x1]][0x1];
	state[0x0][0x2] ^= col[0x2];
	state[0x0][0x2] ^= col[3];
	state[0x1][0x2] = col[0];
	state[1][0x2] ^= gf_mul[col[0x1]][0x0];
	state[1][0x2] ^= gf_mul[col[0x2]][0x1];
	state[0x1][0x2] ^= col[0x3];
	state[0x2][0x2] = col[0];
	state[0x2][0x2] ^= col[0x1];
	state[0x2][2] ^= gf_mul[col[2]][0];
	state[0x2][0x2] ^= gf_mul[col[0x3]][0x1];
	state[3][0x2] = gf_mul[col[0x0]][0x1];
	state[0x3][0x2] ^= col[0x1];
	state[3][0x2] ^= col[0x2];
	state[0x3][0x2] ^= gf_mul[col[3]][0x0];
	
	col[0x0] = state[0x0][0x3];
	col[0x1] = state[0x1][3];
	col[2] = state[2][0x3];
	col[0x3] = state[0x3][0x3];
	state[0x0][0x3] = gf_mul[col[0x0]][0x0];
	state[0x0][0x3] ^= gf_mul[col[0x1]][0x1];
	state[0x0][0x3] ^= col[0x2];
	state[0x0][0x3] ^= col[0x3];
	state[0x1][0x3] = col[0];
	state[0x1][0x3] ^= gf_mul[col[0x1]][0x0];
	state[0x1][3] ^= gf_mul[col[0x2]][1];
	state[0x1][0x3] ^= col[0x3];
	state[0x2][3] = col[0x0];
	state[0x2][0x3] ^= col[0x1];
	state[2][0x3] ^= gf_mul[col[0x2]][0x0];
	state[2][3] ^= gf_mul[col[0x3]][0x1];
	state[0x3][0x3] = gf_mul[col[0x0]][0x1];
	state[0x3][0x3] ^= col[1];
	state[0x3][0x3] ^= col[0x2];
	state[0x3][0x3] ^= gf_mul[col[0x3]][0x0];
}

void w22(BYTE state[][0x4])
{
	BYTE col[0x4];

	col[0x0] = state[0x0][0];
	col[0x1] = state[0x1][0x0];
	col[0x2] = state[0x2][0x0];
	col[0x3] = state[0x3][0x0];
	state[0x0][0x0] = gf_mul[col[0]][0x5];
	state[0x0][0x0] ^= gf_mul[col[0x1]][0x3];
	state[0][0x0] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0] ^= gf_mul[col[0x3]][0x2];
	state[1][0] = gf_mul[col[0x0]][0x2];
	state[0x1][0x0] ^= gf_mul[col[0x1]][5];
	state[0x1][0x0] ^= gf_mul[col[0x2]][0x3];
	state[0x1][0] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x0] = gf_mul[col[0x0]][0x4];
	state[0x2][0] ^= gf_mul[col[0x1]][0x2];
	state[0x2][0x0] ^= gf_mul[col[0x2]][0x5];
	state[0x2][0x0] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x0] = gf_mul[col[0x0]][0x3];
	state[0x3][0x0] ^= gf_mul[col[0x1]][0x4];
	state[0x3][0x0] ^= gf_mul[col[0x2]][0x2];
	state[3][0] ^= gf_mul[col[0x3]][0x5];
	
	col[0] = state[0x0][0x1];
	col[0x1] = state[0x1][0x1];
	col[0x2] = state[0x2][0x1];
	col[3] = state[0x3][0x1];
	state[0x0][0x1] = gf_mul[col[0x0]][5];
	state[0x0][0x1] ^= gf_mul[col[0x1]][3];
	state[0x0][0x1] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x1] ^= gf_mul[col[0x3]][0x2];
	state[0x1][0x1] = gf_mul[col[0]][0x2];
	state[0x1][1] ^= gf_mul[col[0x1]][0x5];
	state[0x1][0x1] ^= gf_mul[col[0x2]][0x3];
	state[0x1][0x1] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x1] = gf_mul[col[0]][0x4];
	state[2][0x1] ^= gf_mul[col[0x1]][0x2];
	state[2][0x1] ^= gf_mul[col[0x2]][0x5];
	state[2][0x1] ^= gf_mul[col[0x3]][3];
	state[0x3][0x1] = gf_mul[col[0x0]][0x3];
	state[3][0x1] ^= gf_mul[col[0x1]][0x4];
	state[0x3][0x1] ^= gf_mul[col[0x2]][0x2];
	state[0x3][0x1] ^= gf_mul[col[0x3]][5];
	
	col[0x0] = state[0x0][0x2];
	col[0x1] = state[0x1][0x2];
	col[0x2] = state[0x2][2];
	col[0x3] = state[0x3][0x2];
	state[0x0][0x2] = gf_mul[col[0x0]][0x5];
	state[0x0][2] ^= gf_mul[col[0x1]][0x3];
	state[0x0][0x2] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x2] ^= gf_mul[col[0x3]][0x2];
	state[0x1][0x2] = gf_mul[col[0]][2];
	state[0x1][0x2] ^= gf_mul[col[1]][0x5];
	state[0x1][0x2] ^= gf_mul[col[0x2]][0x3];
	state[0x1][0x2] ^= gf_mul[col[0x3]][0x4];
	state[0x2][0x2] = gf_mul[col[0x0]][0x4];
	state[0x2][2] ^= gf_mul[col[0x1]][0x2];
	state[0x2][2] ^= gf_mul[col[0x2]][0x5];
	state[2][0x2] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x2] = gf_mul[col[0x0]][0x3];
	state[0x3][0x2] ^= gf_mul[col[0x1]][0x4];
	state[0x3][0x2] ^= gf_mul[col[0x2]][0x2];
	state[0x3][0x2] ^= gf_mul[col[0x3]][5];
	
	col[0x0] = state[0x0][0x3];
	col[0x1] = state[0x1][0x3];
	col[0x2] = state[2][0x3];
	col[0x3] = state[0x3][0x3];
	state[0x0][0x3] = gf_mul[col[0x0]][0x5];
	state[0x0][0x3] ^= gf_mul[col[0x1]][0x3];
	state[0x0][0x3] ^= gf_mul[col[0x2]][0x4];
	state[0x0][0x3] ^= gf_mul[col[0x3]][0x2];
	state[0x1][0x3] = gf_mul[col[0]][0x2];
	state[0x1][0x3] ^= gf_mul[col[0x1]][0x5];
	state[0x1][3] ^= gf_mul[col[0x2]][0x3];
	state[1][0x3] ^= gf_mul[col[3]][0x4];
	state[0x2][0x3] = gf_mul[col[0x0]][0x4];
	state[0x2][0x3] ^= gf_mul[col[0x1]][0x2];
	state[0x2][0x3] ^= gf_mul[col[0x2]][0x5];
	state[0x2][0x3] ^= gf_mul[col[0x3]][0x3];
	state[0x3][0x3] = gf_mul[col[0]][0x3];
	state[0x3][0x3] ^= gf_mul[col[1]][0x4];
	state[3][0x3] ^= gf_mul[col[0x2]][2];
	state[0x3][0x3] ^= gf_mul[col[0x3]][0x5];
}

void blk23(const BYTE in[], BYTE out[], const WORD key[], int keysize)
{
	BYTE state[0x4][4];

	

	
	state[0x0][0x0] = in[0x0];
	state[0x1][0x0] = in[0x1];
	state[2][0x0] = in[2];
	state[0x3][0x0] = in[0x3];
	state[0x0][0x1] = in[0x4];
	state[1][0x1] = in[0x5];
	state[0x2][0x1] = in[6];
	state[0x3][0x1] = in[0x7];
	state[0x0][0x2] = in[0x8];
	state[0x1][0x2] = in[0x9];
	state[0x2][0x2] = in[0xa];
	state[0x3][0x2] = in[0xb];
	state[0x0][3] = in[0xc];
	state[0x1][3] = in[0xd];
	state[0x2][0x3] = in[0xe];
	state[0x3][3] = in[0xf];

	
	v16(state,&key[0x0]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x4]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x8]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0xc]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x10]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[20]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x18]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x1c]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x20]);
	kx17(state); tmp19(state); q21(state); v16(state,&key[0x24]);
	if (keysize != 0x80) {
		kx17(state); tmp19(state); q21(state); v16(state,&key[0x28]);
		kx17(state); tmp19(state); q21(state); v16(state,&key[0x2c]);
		if (keysize != 0xc0) {
			kx17(state); tmp19(state); q21(state); v16(state,&key[48]);
			kx17(state); tmp19(state); q21(state); v16(state,&key[0x34]);
			kx17(state); tmp19(state); v16(state,&key[56]);
		}
		else {
			kx17(state); tmp19(state); v16(state,&key[0x30]);
		}
	}
	else {
		kx17(state); tmp19(state); v16(state,&key[40]);
	}

	out[0x0] = state[0x0][0x0];
	out[0x1] = state[0x1][0x0];
	out[0x2] = state[0x2][0x0];
	out[0x3] = state[0x3][0x0];
	out[0x4] = state[0x0][0x1];
	out[0x5] = state[0x1][0x1];
	out[6] = state[0x2][0x1];
	out[0x7] = state[3][0x1];
	out[0x8] = state[0x0][0x2];
	out[0x9] = state[0x1][0x2];
	out[0xa] = state[0x2][0x2];
	out[0xb] = state[0x3][0x2];
	out[0xc] = state[0x0][0x3];
	out[0xd] = state[0x1][0x3];
	out[0xe] = state[0x2][0x3];
	out[0xf] = state[3][0x3];
}

void h024(const BYTE in[], BYTE out[], const WORD key[], int keysize)
{
	BYTE state[0x4][0x4];

	state[0x0][0x0] = in[0x0];
	state[0x1][0] = in[0x1];
	state[2][0x0] = in[0x2];
	state[0x3][0x0] = in[0x3];
	state[0][0x1] = in[4];
	state[1][0x1] = in[0x5];
	state[0x2][0x1] = in[6];
	state[3][0x1] = in[0x7];
	state[0x0][0x2] = in[0x8];
	state[0x1][0x2] = in[9];
	state[0x2][0x2] = in[0xa];
	state[3][2] = in[0xb];
	state[0][0x3] = in[0xc];
	state[0x1][0x3] = in[0xd];
	state[0x2][0x3] = in[0xe];
	state[0x3][0x3] = in[15];

	
	if (keysize > 128) {
		if (keysize > 0xc0) {
			v16(state,&key[0x38]);
			r20(state);z18(state);v16(state,&key[0x34]);w22(state);
			r20(state);z18(state);v16(state,&key[0x30]);w22(state);
		}
		else {
			v16(state,&key[0x30]);
		}
		r20(state);z18(state);v16(state,&key[0x2c]);w22(state);
		r20(state);z18(state);v16(state,&key[40]);w22(state);
	}
	else {
		v16(state,&key[0x28]);
	}
	r20(state);z18(state);v16(state,&key[0x24]);w22(state);
	r20(state);z18(state);v16(state,&key[0x20]);w22(state);
	r20(state);z18(state);v16(state,&key[0x1c]);w22(state);
	r20(state);z18(state);v16(state,&key[0x18]);w22(state);
	r20(state);z18(state);v16(state,&key[0x14]);w22(state);
	r20(state);z18(state);v16(state,&key[0x10]);w22(state);
	r20(state);z18(state);v16(state,&key[12]);w22(state);
	r20(state);z18(state);v16(state,&key[0x8]);w22(state);
	r20(state);z18(state);v16(state,&key[0x4]);w22(state);
	r20(state);z18(state);v16(state,&key[0x0]);

	out[0x0] = state[0][0x0];
	out[0x1] = state[0x1][0x0];
	out[0x2] = state[0x2][0x0];
	out[3] = state[0x3][0x0];
	out[0x4] = state[0x0][0x1];
	out[0x5] = state[0x1][0x1];
	out[6] = state[0x2][0x1];
	out[0x7] = state[0x3][0x1];
	out[8] = state[0][0x2];
	out[0x9] = state[0x1][0x2];
	out[0xa] = state[0x2][0x2];
	out[0xb] = state[0x3][0x2];
	out[12] = state[0x0][0x3];
	out[0xd] = state[0x1][0x3];
	out[0xe] = state[0x2][3];
	out[0xf] = state[3][0x3];
}

