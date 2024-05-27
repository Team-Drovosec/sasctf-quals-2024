use std::fs::File;

use fastnbt::Value;
use mca_parser::Region;

const HEIGHT_START: i64 = -64;
const HEIGHT_END: i64 = 100;
const HEIGHT: usize = (HEIGHT_END - HEIGHT_START + 1) as usize;
const WIDTH: usize = HEIGHT;
const SIGN_WIDTH: i32 = 10;
const SIGN_HEIGHT: i32 = 4;
const DATA_WIDTH: usize = SIGN_WIDTH as usize * WIDTH;
const DATA_HEIGHT: usize = SIGN_HEIGHT as usize * HEIGHT;

fn main2() -> Result<(), mca_parser::error::Error> {
    // Create a Region from an open file
    let mut file = File::open("./signed/region/r.0.0.mca")?;
    let mut text_data = [['\0'; DATA_WIDTH + 300]; DATA_HEIGHT];
    let region = Region::from_reader(&mut file)?;

    // `chunk` is raw chunk data, so we need to parse it
    for chunk_z in 0..9 {
        let chunk = region.get_chunk(0, chunk_z)?;
        if let Some(chunk) = chunk {
            // Parse the raw chunk data into structured NBT format
            let parsed = chunk.parse()?;
            for v in &parsed.block_entities {
                if let Value::Compound(comp) = v {
                    match (
                        comp.get("x"),
                        comp.get("y"),
                        comp.get("z"),
                        comp.get("front_text"),
                    ) {
                        (
                            Some(Value::Int(0)),
                            Some(Value::Int(y)),
                            Some(Value::Int(z)),
                            Some(Value::Compound(front_text)),
                        ) => {
                            let block_z = z;
                            let data_x = block_z * SIGN_WIDTH;
                            let data_y = (y - (-64)) * SIGN_HEIGHT;
                            println!("{:?} {:?} ({:?}) {:?} {:?}", y, block_z, z, data_x, data_y);
                            if let Some(Value::List(messages)) = front_text.get("messages") {
                                match &messages[..] {
                                    [Value::String(line1), Value::String(line2), Value::String(line3), Value::String(line4)] =>
                                    {
                                        println!(
                                            "{:?} {:?} {:?} {:?} {:?} {:?}",
                                            y, block_z, line1, line2, line3, line4
                                        );
                                        for (linen, lined) in
                                            [(3, line1), (2, line2), (1, line3), (3, line4)]
                                        {
                                            text_data[data_y as usize + linen]
                                                [data_x as usize..(data_x + SIGN_WIDTH) as usize]
                                                .copy_from_slice(
                                                    &lined[1 as usize..(1 + SIGN_WIDTH) as usize]
                                                        .chars()
                                                        .collect::<Vec<char>>()
                                                        .as_slice(),
                                                );
                                        }
                                    }
                                    _ => {}
                                }
                            }
                        }
                        _ => {}
                    }
                }
            }
        } else {
            // If the chunk is None, it has not been generated
            println!("Chunk has not been generated.");
        }
    }
    println!("{:}", text_data.iter().rev().map(|line| line.iter().collect::<String>()).fold(String::new(), |a, b| a + &b + "\n"));
    Ok(())
}

fn main() {
    match main2() {
        Ok(_) => {}
        Err(e) => eprintln!("Error: {:#?}", e),
    }
}
