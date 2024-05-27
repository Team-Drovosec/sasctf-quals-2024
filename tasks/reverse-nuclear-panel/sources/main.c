#include "generated.h"

void RC4(unsigned char *data, int dataLen, unsigned char *key, int keyLen, unsigned char *result) {
    unsigned char T[256];
    unsigned char S[256];
    unsigned char tmp;

    for (int i = 0; i < 256; i++) {
        S[i] = i;
        T[i] = key[i % keyLen];
    }

    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + T[i]) % 256;

        tmp = S[j];
        S[j] = S[i];
        S[i] = tmp;
    }
    int i = 0;
    j = 0;
    for (int x = 0; x < dataLen; x++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;

        tmp = S[j];
        S[j] = S[i];
        S[i] = tmp;

        int t = (S[i] + S[j]) % 256;

        result[x] = data[x] ^ S[t];
    }
}

union UIntByteUnion {
    unsigned int uint;
    unsigned char uchars[4];
};

union EightByTwoBytes {
    unsigned char uchars[8];
    unsigned short ushorts[4];
};


unsigned int fib(unsigned int n) { 
    unsigned int a = 0, b = 1, c, i; 
    if (n == 0) {
        return a;
    }
    for (i = 2; i <= n; i++) { 
        c = a + b; 
        a = b; 
        b = c; 
    } 
    return b; 
} 

int check1(unsigned char *data) {
  if (data[0] == 0xb7 && data[1] == 0x24 && data[2] == 0x60 && data[3] == 0x05 && \
      data[4] == 0x35 && data[5] == 0x31 && data[6] == 0x69 && data[7] == 0x72)
      return 1;

  return 0;
}

int check2(unsigned char *data) {
    unsigned char xorData[] = {0x05, 0xaa, 0x32, 0xad, 0xb4, 0x15, 0x20, 0x8f};
    unsigned char goodData[] = {0x28, 0x19, 0xf3, 0x59, 0x7d, 0x42, 0x16, 0xcb};
    for (int i = 0; i < 8; ++i) {
        unsigned char a = xorData[i] ^ data[i];
        if (a != goodData[i])
            return 0;
    }

    return 1;
}

int check3(unsigned char *data) {
    unsigned int goodData = fib(46);
    union UIntByteUnion dataUnion;
    for (int i = 0; i < 4; ++i) {
        dataUnion.uchars[i] = data[i];
    }

    if (dataUnion.uint == goodData)
        return 1;
    
    return 0;
}

int check4(unsigned char *data) {
    unsigned int k = 11;
    unsigned int a = 1773419894;
    unsigned int b = 211049538;
    union UIntByteUnion dataUnion;
    for (int i = 0; i < 4; ++i) {
        dataUnion.uchars[i] = data[i];
    }

    if (k * dataUnion.uint - a == b) {
        return 1;
    }

    return 0;
}

int check5(unsigned char *data) {
    unsigned int dataA[] = {17, 18, 26, 2};
    unsigned int dataB[] = {68822, 54112, 97415, 15262};
    unsigned int dataC[] = {9, 32, 29, 8};
    unsigned int dataD[] = {20234, 53240, 86439, 92013};
    unsigned int dataE[] = {3116702, 29881528, 36888976, 445485};

    union EightByTwoBytes dataUnion;
    for (int i = 0; i < 8; ++i) {
        dataUnion.uchars[i] = data[i];
    }

    for (int i = 0; i < 4; ++i) {
        if ((dataA[i] * dataUnion.ushorts[i] + dataB[i]) * dataC[i] + dataD[i] != dataE[i]) {
            return 0;
        }
    }
    return 1;
}

unsigned char hacked[60];
char* perform_hack(unsigned char *key) {
    unsigned char flag[] = {0xc7,0xc9,0x6e,0x78,0xe9,0x9b,0x85,0xf2,0x13,0x6d,0x32,0x33,0x40,0x3d,0x0c,0xba,0x15,0xc1,0x1f,0x03,0x15,0xb1,0x68,0x45,0xd6,0xb3,0xee,0x69,0xd9,0xca,0x4a,0x2b,0x2c,0x6b,0x0c,0xd6,0x9b,0x38,0x27,0xfa,0x3e,0xcd,0x4a,0x1f,0xcf,0xd7,0x0e,0x36,0xfd,0xa7,0xc3,0x7b,0x69,0x0b,0x57,0x3c,0xce,0xfa,0xef,0xff};
    
    RC4(flag, sizeof(flag), key, 64, hacked);
    return (char*)hacked;
}
