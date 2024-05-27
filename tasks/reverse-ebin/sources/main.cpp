#include <iostream>

void xorstr(char* key, char* text_ptr, int length) {
	int key_length = 0;
	for (; key[key_length] != 0; key_length++) {}
	for (int i = 0; i < length; i++) {
		text_ptr[i] ^= key[i % key_length];
	}
}

void xorshcode(char* junk_ptr, int length) {
	char* key = junk_ptr + 35;
	char* text_ptr = junk_ptr + 25 + ((int)(junk_ptr[22]) << 8) + junk_ptr[21];
	int key_length = 0;
	for (; key[key_length] != 0; key_length++) {}
	for (int i = 0; i < length; i++) {
		text_ptr[i] ^= key[i % key_length];
	}
}


void part1(char* input) {
	int a = 1, b = 2, c = 0;
	for (int i = 0; i < 25; i++) {
		c = a;
		a = b;
		b += c;
		input[i % 8] ^= b;
	}
}


uint32_t rotate_right(uint32_t v, uint32_t n) {
	n &= 0x1f;
	return (v >> n) | (v << (32 - n));
}

void encrypt(uint32_t S[26], uint32_t inout[4]) {
	for (uint32_t i = 0; i < 4; i += 2) {
		uint32_t A = inout[i];
		uint32_t B = inout[i + 1];
		A += S[0];
		B += S[1];
		for (int j = 0; j < 12; ++j) {
			A = (((A ^ B) << (B & 0x1f)) | ((A ^ B) >> (32 - (B & 0x1f)))) + S[2 * i];
			B = (((B ^ A) << (A & 0x1f)) | ((B ^ A) >> (32 - (A & 0x1f)))) + S[2 * i + 1];
		}
		inout[i] = A;
		inout[i + 1] = B;
	}
}

void decrypt(uint32_t S[26], uint32_t inout[4]) {
	for (uint32_t i = 0; i < 4; i += 2) {
		uint32_t A = inout[i];
		uint32_t B = inout[i + 1];
		for (int j = 12; j > 0; --j) {
			B = rotate_right(B - S[2 * i + 1], A) ^ A;
			A = rotate_right(A - S[2 * i], B) ^ B;
		}
		B -= S[1];
		A -= S[0];
		inout[i] = A;
		inout[i + 1] = B;
	}
}
	
void expand(uint32_t L[4], uint32_t S[26]) {
	uint32_t A = 0;
	uint32_t B = 0;
	uint32_t i = 0;
	uint32_t j = 0;
	S[0] = 0xb7e15163;
	for (i = 1; i < 26; ++i)
		S[i] = S[i - 1] + 0x9e3779b9;
	i = j = 0;
	int n = 3 * 26;
	while (n-- > 0) {
		A = S[i] = ((S[i] + A + B) << (3 & 0x1f)) | ((S[i] + A + B) >> (32 - (3 & 0x1f)));
		B = L[j] = ((L[j] + A + B) << ((A + B) & 0x1f)) | ((L[j] + A + B) >> (32 - ((A + B) & 0x1f)));
		i = (i + 1) % 26;
		j = (j + 1) % 4;
	}
}

int test(uint32_t S[26], uint32_t messg[4]) {
	uint32_t save[4];
	memcpy(save, messg, sizeof save);
	encrypt(S, messg);
	decrypt(S, messg);
	for (int i = 0; i < 4; ++i) {
		if (messg[i] != save[i])
			return 0;
	}
	return 1;
}

/*int main() {
	uint32_t key[4] = { 0x243F6A88, 0x85A308D3, 0x452821E6, 0x38D01377 };
	uint32_t box[26];
	expand(key, box);

	uint32_t message[4] = { 0xfeedface, 0xdeadbeef, 0xfeedbabe, 0xcafebeef };

	for (int i = 0; i < 43690; ++i)
		if (!test(box, message))
			return 1;
	return 0;
}*/

int main() {
	char text[] = "teststringabab";
	part1(text);
	std::cout << text << std::endl;

	return 0;
}