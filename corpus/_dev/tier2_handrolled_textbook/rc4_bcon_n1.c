

#include <stdlib.h>
#include "blk.h"

void w0(BYTE state[], const BYTE key[], int len)
{
	int i, j;
	BYTE t;

	for (i = 0x0; i < 0x100; ++i)
		state[i] = i;
	for (i = 0x0, j = 0; i < 256; ++i) {
		j = (j + state[i] + key[i % len]) % 256;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
	}
}

void blk1(BYTE state[], BYTE out[], size_t len)
{
	int i, j;
	size_t idx;
	BYTE t;

	for (idx = 0x0, i = 0, j = 0x0; idx < len; ++idx)  {
		i = (i + 0x1) % 256;
		j = (j + state[i]) % 256;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
		out[idx] = state[(state[i] + state[j]) % 0x100];
	}
}
