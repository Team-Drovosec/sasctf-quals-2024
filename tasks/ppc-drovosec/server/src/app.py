import asyncio
import logging

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI, HTTPException, Request

from src.connections import (
    CONNECTIONS,
    MAX_CONNS,
    add_connection,
    check_in,
    get_connections,
    is_rate_limited,
    remove_connection,
    reset_connections,
)
from src.game_track import GameTrack
from src.schemas import Offer

app = FastAPI()

# my_own_handler = logging.StreamHandler()
# my_own_handler.setLevel(logging.DEBUG)
# my_own_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # Users can use logging format preferable for them
# my_own_handler.setFormatter(my_own_formatter)
#
# aiortc_logger = logging.getLogger("aiortc")
# aiortc_logger.addHandler(my_own_handler)
# aiortc_logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.WARNING)


def configure_connection(pc: RTCPeerConnection):
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        # print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            CONNECTIONS.discard(pc)
            remove_connection()

    game_track = GameTrack(pc)
    pc.addTrack(game_track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        # print("created by remote party")
        game_track.init_channel(channel)

        @channel.on("message")
        def on_message(message):
            game_track.pressed_keys.append(message)


@app.post("/offer")
async def create_offer(offer: Offer, request: Request) -> Offer:
    offer = RTCSessionDescription(sdp=offer.sdp, type=offer.type)

    connection = RTCPeerConnection()

    ip = request.headers.get("x-envoy-external-address", request.client.host)

    conns = get_connections()
    if conns > MAX_CONNS:
        logging.error(f"MAX CONNS REACHED DID NOT GAVE CONNECTION TO {ip} {request.headers=}")
        raise HTTPException(status_code=500, detail="The server has reached it's limit for connections. Try connecting later.")
    
    if is_rate_limited(ip):
        logging.error(f"TIME LIMITED {ip} {request.headers=}")
        raise HTTPException(status_code=403, detail="Not so fast. Try again in 15 secons")

    logging.error(f"SUCCESSFULLY GIVEN CONNECTION TO {ip} {request.headers=}")

    CONNECTIONS.add(connection)
    add_connection()
    check_in(ip)

    configure_connection(connection)

    await connection.setRemoteDescription(offer)

    answer = await connection.createAnswer()
    await connection.setLocalDescription(answer)

    return Offer(sdp=connection.localDescription.sdp, type=connection.localDescription.type)


@app.on_event("shutdown")
async def shutdown_event():
    await asyncio.gather(*(pc.close() for pc in CONNECTIONS))
    CONNECTIONS.clear()
    reset_connections()
