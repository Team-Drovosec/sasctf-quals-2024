import math

from PIL.Image import Image
from aiortc import RTCPeerConnection

from src.connections import CONNECTIONS


def resize_image(image: Image, *, new_width: int | None = None, new_height: int | None = None) -> Image:
    width, height = image.size

    if new_height:
        ratio = width / height
        return image.resize((int(new_height * ratio), new_height))

    ratio = height / width

    return image.resize((new_width, int(new_width * ratio)))


async def close_connection(pc: RTCPeerConnection):
    pc.remove_all_listeners()
    CONNECTIONS.discard(pc)


def stepped_function(x):
    result = x
    for i in range(4):
        result -= math.sin(result)
    return result
