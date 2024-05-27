import asyncio

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI

from src.connections import CONNECTIONS
from src.game_track import GameTrack
from src.schemas import Offer

app = FastAPI()


def configure_connection(pc: RTCPeerConnection):
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            await pc.close()
            CONNECTIONS.discard(pc)

    game_track = GameTrack(pc)
    pc.addTrack(game_track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        game_track.init_channel(channel)

        @channel.on("message")
        def on_message(message):
            game_track.pressed_keys.append(message)


@app.post("/offer")
async def create_offer(offer: Offer) -> Offer:
    offer = RTCSessionDescription(sdp=offer.sdp, type=offer.type)

    connection = RTCPeerConnection()
    CONNECTIONS.add(connection)

    configure_connection(connection)

    await connection.setRemoteDescription(offer)

    answer = await connection.createAnswer()
    await connection.setLocalDescription(answer)

    return Offer(sdp=connection.localDescription.sdp, type=connection.localDescription.type)


@app.on_event("shutdown")
async def shutdown_event():
    await asyncio.gather(*(pc.close() for pc in CONNECTIONS))
    CONNECTIONS.clear()
