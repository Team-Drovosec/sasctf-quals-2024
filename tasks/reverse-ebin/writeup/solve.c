#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

uint32_t shift_left(uint32_t v, uint32_t n) {
	return v << n;
}

uint32_t shift_right(uint32_t v, uint32_t n) {
	return v >> n;
}

uint32_t rotate_left(uint32_t v, uint32_t n) {
	n &= 0x1f;
	return shift_left(v, n) | shift_right(v, 32 - n);
}

uint32_t rotate_right(uint32_t v, uint32_t n) {
	n &= 0x1f;
	return shift_right(v, n) | shift_left(v, 32 - n);
}

void encrypt(uint32_t S[26], uint32_t inout[4]) {
	for (uint32_t i = 0; i < 4; i += 2) {
		uint32_t A = inout[i];
		uint32_t B = inout[i+1];
		A += S[0];
		B += S[1];
		for (int j = 0; j < 12; ++j) {
			A = rotate_left((A ^ B), B) + S[2 * i];
			B = rotate_left((B ^ A), A) + S[2 * i + 1];
		}
		inout[i] = A;
		inout[i+1] = B;
	}
}

void decrypt(uint32_t S[26], uint32_t inout[4]) {
	for (uint32_t i = 0; i < 4; i += 2) {
		uint32_t A = inout[i];
		uint32_t B = inout[i+1];
		for (int j = 12; j > 0; --j) {
			B = rotate_right(B - S[2 * i + 1], A) ^ A;
			A = rotate_right(A - S[2 * i], B) ^ B;
		}
		B -= S[1];
		A -= S[0];
		inout[i] = A;
		inout[i+1] = B;
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
	int n = 3*26;
	while (n-- > 0) {
		A = S[i] = rotate_left((S[i] + A + B), 3);
		B = L[j] = rotate_left((L[j] + A + B), A + B);
		i = (i + 1) % 26;
		j = (j + 1) % 4;
	}
}


void uint64_to_byte_array(uint64_t value, uint8_t *byte_array) {
    for (int i = 0; i < 8; ++i) {
        byte_array[i] = (value >> (i * 8)) & 0xFF;
    }
}


void uint32_to_uint64_arr(uint32_t input[], uint64_t output[]) {
    output[0] = ((uint64_t) input[0]) <<  0 | ((uint64_t) input[1] << 32);
    output[1] = ((uint64_t) input[2]) <<  0 | ((uint64_t) input[3] << 32);
    output[2] = ((uint64_t) input[4]) <<  0 | ((uint64_t) input[5] << 32);
}

void print_chr_array(const unsigned char *array, size_t size) {
    for (size_t i = 0; i < size; i++) {
        printf("%c", (char) array[i]); 
    }
    printf("\n");
}

void gen_variants(unsigned char *array, size_t size, size_t index) {
    if (index == size) {
        print_chr_array(array, size);
        return;
    }

    array[index] ^= 0x01; 
    gen_variants(array, size, index + 1); 
    array[index] ^= 0x01; 
    gen_variants(array, size, index + 1); 
}


void eberse_drift(uint8_t *array) {
    uint8_t tmp[8];
    for (size_t i = 0; i < 8; ++i) {
        tmp[i] = array[i] - (array[i] >> 5);
    }
    for (size_t i = 0; i < 8; ++i) {
	array[i] = tmp[7 - i]; 
    }
}

void ebonatto(uint8_t *array) {
	int a = 1, b = 2, c = 0;
	for (int i = 0; i < 25; i++) {
		c = a;
		a = b;
		b += c;
		array[i % 8] ^= b;
	}
}

void dibide(uint8_t *array) {
    for (size_t i = 0; i < 8; ++i) {
        array[i] *= 2;
    }
}

int main() {
	uint32_t checksum[6] = {0x0e67f93a, 0x31c4b906, 0x6e8dfb75, 0x22e6e190, 0xc86aff5c, 0xaaff2ed5};	
	uint32_t part1_x2[4] = { checksum[0],  checksum[1], checksum[0], checksum[1]};
        uint32_t box[26];
        uint32_t part2_3[4] = {checksum[2], checksum[3], checksum[4], checksum[5]};

        expand(part1_x2, box);	
        decrypt(box, part2_3);

	uint32_t part3_x2[4] = { part2_3[2], part2_3[3], part2_3[2], part2_3[3]};
	uint32_t box2[26];
	uint32_t part1_2[4] = {checksum[0], checksum[1], part2_3[0], part2_3[1]};

	expand(part3_x2, box2);
	decrypt(box2, part1_2);
	
	uint64_t decrypted_parts_uint64[3];
	uint32_t decrypted_parts_uint32[6] = {part1_2[0], part1_2[1], part1_2[2], part1_2[3], part2_3[2], part2_3[3]};
	uint32_to_uint64_arr(decrypted_parts_uint32, decrypted_parts_uint64);
	
	uint8_t parts[3][8];
	for (int i = 0; i < 3; i++) {
		uint64_to_byte_array(decrypted_parts_uint64[i], parts[i]);
	}
	
	ebonatto(parts[0]);
	dibide(parts[1]);
	eberse_drift(parts[2]);
	
	printf("Part 1: SAS{");
	print_chr_array((unsigned char *) parts[0], 8);
	printf("Part 3: ");
	print_chr_array((unsigned char *) parts[2], 8);
	printf("Part 2: ");
    	print_chr_array(parts[1], 8);
    	printf("Possible variants for the Part 2:\n");
    	gen_variants(parts[1], 8, 0);		
	return 0;
}
