import asyncio
import sys

import asyncio
import logging

import logging
import asyncio
import sys

import task
import random

root_logger = logging.getLogger("grades")
root_logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("[%(asctime)s] [%(name)8s] [%(levelname)-5.5s] --- %(message)s")

file_handler = logging.FileHandler("./latest.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

TOTAL = 25
FLAG = "SAS{mi_flue_parolas_koditan_esperanton}"

async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    host, port = writer.get_extra_info('peername')
    logger = root_logger.getChild(f"{host}:{port}")
    logger.info("Connection opened from %s", writer.get_extra_info('peername'))
    writer.write(f"Ĉiu simbolo estas anstataŭigita per alia hazarda simbolo. Deĉifri {TOTAL} tekstojn.\n".encode())
    random.seed()
    s = random.randint(0, 10000) * 100
    solved = 0
    while solved < TOTAL and not writer.is_closing():
        logger.info(f"solved {solved} taks")
        writer.write(f"Ĉifrita {solved} teksto{'j' if solved == 1 else ''}\n".encode())
        try:
            logger.info("Making task %s", s + solved)
            task_s, task_answer = task.make_task(s + solved)
            writer.write(task_s.encode() + b'\n')
            try:
                async with asyncio.timeout(60):
                    line = await reader.readuntil()
            except TimeoutError:
                logger.info("Timeout")
                writer.write("Tro malrapida\n".encode())
                break
            logger.info(f"{len(line)} bytes received")
            correct = line.decode().strip() == task_answer.strip()
            logger.debug("received %s", line.decode().strip())
            logger.debug("expected %s", task_answer.strip())
            if correct:
                solved += 1
                writer.write("Ĝuste\n".encode())
                logger.info("correct")
            else:
                writer.write("Malkorekta\n".encode())
                logger.info("incorrect")
                break
        except Exception as e:
            writer.write("Neatendita eraro\n".encode())
            logger.error(e)
            break
    if solved >= TOTAL:
        logger.info("solved")
        flag = FLAG
        writer.write(f"Via flago: {flag}\n".encode())
    writer.write(f"Adiaŭ!\n".encode())
    writer.write_eof()
    await writer.wait_closed()

async def main(host="127.0.0.1", port=8888, **kwargs):
    server = await asyncio.start_server(handle_connection, host, port, **kwargs)

    addr = server.sockets[0].getsockname()
    root_logger.info("Serving on %s", addr)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], int(sys.argv[2])))