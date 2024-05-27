
use std::io::{self, BufRead, Write};

const FLAG_ENC: [u8; 69] = [0x79,0x41,0x69,0xa2,0xae,0x0b,0x56,0x4b,0x3c,0xa2,0xfb,0xb0,0x4e,0xb0,0xef,0xff,0x55,0x84,0x7d,0x6d,0x58,0xd8,0x84,0x48,0x9d,0x45,0x81,0x1a,0xad,0x25,0x89,0x12,0x6b,0xd1,0x32,0x42,0x70,0xba,0xe2,0x92,0x76,0x57,0x41,0x83,0xe3,0x00,0x57,0x2b,0x58,0xb4,0x95,0x3a,0x42,0x63,0xf0,0xf8,0xf9,0x62,0xf9,0x18,0xc0,0x00,0xed,0xed,0x77,0xfb,0x55,0x65,0x6b];
const ALPHABET_S: [(u8, f64, f64); 7] = [
    (97, 0f64, 0.14285714285714285f64),
    (104, 0.14285714285714285f64, 0.23809523809523808f64),
    (107, 0.23809523809523808f64, 0.3333333333333333f64),
    (109, 0.3333333333333333f64, 0.42857142857142855f64),
    (110, 0.42857142857142855f64, 0.5238095238095237f64),
    (112, 0.5238095238095237f64, 0.5714285714285714f64),
    (117, 0.5714285714285714f64, 1f64),
];

fn main() {
    print!("Enter password: ");
    io::stdout().flush().unwrap();
    let mut line = String::new();
    io::stdin().lock().read_line(&mut line).unwrap();
    line.truncate(line.trim_end().len());

    let fail = || {
        println!("Invalid password");
        std::process::exit(1);
    };
    if line.len() == 21 {
        // let mut ALPHABET_S = core::array::from_fn::<_, 7, _>(|_| (0u8, 0f64, 0f64));
        // let mut alphabet = core::array::from_fn::<_, 256, _>(|_| (0f64, 0f64));
        // for i in line.bytes() {
        //     alphabet[i as usize].0 += 1f64;
        // }
        // let mut cur = 0;
        // let mut current = 0f64;
        // for (char, (left, right)) in alphabet.iter_mut().enumerate() {
        //     *right = &current + &*left / line.len() as f64;
        //     *left = current;
        //     current = *right;
        //     if *right - *left != 0f64 {
        //         ALPHABET_S[cur] = (char.try_into().unwrap(), *left, *right);
        //         cur += 1usize;
        //     }
        // }
        // for (char, left, right) in ALPHABET_S.iter() {
        //     println!("({}, {}f64, {}f64),", char, left.to_string(), right.to_string());
        // }
        let mut left = 0f64;
        let mut right = 1f64;
        for i in line.bytes() {
            if let Ok(index) = ALPHABET_S.binary_search_by_key(&i, |tpl| tpl.0) {
                let range = &ALPHABET_S[index];
                let new_left = &left + (&right - &left) * &range.1;
                let new_right = &left + (&right - &left) * &range.2;
                left = new_left;
                right = new_right;
            } else {
                fail();
            }
        }
        let result = (left + right) / 2f64;
        // let mut vec = vec![0u8;line.len()];
        // let mut left = 0f64;
        // let mut right = 1f64;
        // for i in vec.iter_mut() {
        //     if let Err(index) = ALPHABET_S.binary_search_by(|probe| {
        //         let val = left + (right - left) * &probe.1;
        //         val.total_cmp(&result)
        //     }) {
        //         *i = ALPHABET_S[index-1].0;
        //         let new_left = &left + (&right - &left) * ALPHABET_S[index-1].1.clone();
        //         let new_right = &left + (&right - &left) * ALPHABET_S[index-1].2.clone();
        //         left = new_left;
        //         right = new_right;
        //     }
        // };
        // println!("{}", result.to_string());
        // assert_eq!(String::from_utf8(vec).unwrap(), line);
        if result == 0.21346205453617723 {
            let mut t = [0u8; 256];
            let mut s = [0u8; 256];
            for i in 0..256 {
                s[i] = i as u8;
                t[i] = line.as_bytes()[i % line.bytes().len()];
            }
            let mut j: usize = 0;
            for i in 0..256 {
                j = (j + s[i] as usize + t[i] as usize) % 256;
                s.swap(i, j);
            }

            let mut flag = FLAG_ENC.clone();
            let mut i: usize = 0;
            let mut j: usize = 0;
            for chr in flag.iter_mut() {
                i = (i + 1) % 256;
                j = (j + s[i] as usize) % 256;
                
                s.swap(i, j);
                *chr ^= s[(s[i] as usize + s[j] as usize) % 256];
            }
            println!("Flag is: {}", String::from_utf8_lossy(&flag));
            std::process::exit(0);
        }
    }
    fail();
}
