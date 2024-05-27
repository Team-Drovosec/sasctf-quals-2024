import asyncio
from enum import IntEnum
from functools import partial
from math import ceil

import cv2
import numpy as np
import requests
from aiortc import RTCDataChannel, RTCPeerConnection, RTCSessionDescription
from aiortc.rtcrtpreceiver import RemoteStreamTrack

URL = "https://ppc_drovosec.task.sasc.tf/offer"

SPAWN_ZONE_SIZE = (48, 38)
SPAWN_ZONE_COORDINATES = [
    (0, 362),
    (1231, 362),
    (0, 528),
    (1231, 528),
]

DIFF_THRESHOLD = 40

KEY_MAPPING = {
    0: ("a", "w", "attack"),
    1: ("d", "w", "attack"),
    2: ("a", "s", "attack"),
    3: ("d", "s", "attack"),
}

DATA_CHANNEL_OPENED = False
ATTACK_FRAMES = 3

ATTACK_QUEUE = []
OBJECT_IN_SPAWN_ZONE = {0: None, 1: None, 2: None, 3: None}
LAST_SPEED_ON_PLATFORM = [
    0,
    0,
    0,
    0,
]  # sometimes compression artifacts can have significant effect on the speed estimation
SPEED_ANOMALY_TOLERANCE = 100
LEFT_LENGTH = 607
RIGHT_LENGTH = 530


def get_diff(array1: np.array, array2: np.array) -> np.array:
    diff = np.abs(array1.astype("int8") - array2.astype("int8"))
    diff = np.where(diff > DIFF_THRESHOLD, diff, 0)

    return diff


def frames_ETA(elapsed_frames, platform_length):
    return ceil(
        (platform_length - SPAWN_ZONE_SIZE[0]) / (SPAWN_ZONE_SIZE[0] / elapsed_frames)
        - ATTACK_FRAMES
    )


def get_mean_color(zone: np.array):
    return np.mean(zone, axis=(0, 1))


class Target(IntEnum):
    LOG = 0
    BEAVER = 1


FRAME_NUMBER = 0
COLOR_TOLERANCE = 30
LOG_MEANS = [
    np.array([170.17050439, 139.73355263, 94.71710526]),
    np.array([171.6622807, 140.15625, 95.37719298]),
    np.array([198.65789474, 149.16502193, 111.4566886]),
    np.array([161.69024123, 150.01315789, 88.21107456]),
]


def process_positions(diff: np.array, current_frame: np.array) -> None:
    global FRAME_NUMBER
    for i, (x, y) in enumerate(SPAWN_ZONE_COORDINATES):
        zone = diff[y : y + SPAWN_ZONE_SIZE[1], x : x + SPAWN_ZONE_SIZE[0]]
        if not OBJECT_IN_SPAWN_ZONE[i] and np.count_nonzero(zone) < 600:
            continue

        if OBJECT_IN_SPAWN_ZONE[i] and np.count_nonzero(zone) < 140:
            if OBJECT_IN_SPAWN_ZONE[i][2] == Target.LOG:
                frame_estimation = frames_ETA(
                    FRAME_NUMBER - OBJECT_IN_SPAWN_ZONE[i][0],
                    RIGHT_LENGTH if i in (1, 3) else LEFT_LENGTH,
                )

                if (
                    LAST_SPEED_ON_PLATFORM[i]
                    and abs(LAST_SPEED_ON_PLATFORM[i] - frame_estimation)
                    > SPEED_ANOMALY_TOLERANCE
                ):
                    print("THE LOG IS SPEEDING HIGH HOLY FUCK!!!", frame_estimation)
                    frame_estimation = LAST_SPEED_ON_PLATFORM[i]
                else:
                    LAST_SPEED_ON_PLATFORM[i] = frame_estimation

                OBJECT_IN_SPAWN_ZONE[i][0] = frame_estimation
                ATTACK_QUEUE.append([i, FRAME_NUMBER + frame_estimation])

            print(i, OBJECT_IN_SPAWN_ZONE[i])
            OBJECT_IN_SPAWN_ZONE[i] = None
        elif not OBJECT_IN_SPAWN_ZONE[i]:
            mean_color = get_mean_color(
                current_frame[y : y + SPAWN_ZONE_SIZE[1], x : x + SPAWN_ZONE_SIZE[0]]
            )
            if np.linalg.norm(mean_color - LOG_MEANS[i]) < COLOR_TOLERANCE:
                OBJECT_IN_SPAWN_ZONE[i] = [FRAME_NUMBER, mean_color, Target.LOG]
            else:
                OBJECT_IN_SPAWN_ZONE[i] = [0, mean_color, Target.BEAVER]


REFERENCE_FRAME = None


async def data_handler(stream: RemoteStreamTrack, data_channel: RTCDataChannel):
    global FRAME_NUMBER
    global REFERENCE_FRAME

    while frame := (await stream.recv()).to_image():
        FRAME_NUMBER += 1

        frame_as_array = np.array(frame, dtype="uint8")

        cv2.imshow("Game", frame_as_array)
        cv2.waitKey(1)

        if REFERENCE_FRAME is None and FRAME_NUMBER == 20:
            REFERENCE_FRAME = frame_as_array
        if not DATA_CHANNEL_OPENED:
            continue

        if REFERENCE_FRAME is not None:
            diff = get_diff(REFERENCE_FRAME, frame_as_array)
            if np.count_nonzero(diff) < 210000:  # skip fucked up frames
                process_positions(diff, frame_as_array)

            if ATTACK_QUEUE:
                if FRAME_NUMBER == ATTACK_QUEUE[0][1]:
                    for key in KEY_MAPPING[ATTACK_QUEUE.pop(0)[0]]:
                        data_channel.send(key)


async def main():
    pc = RTCPeerConnection()

    dc = pc.createDataChannel("DROVOSEC")

    @dc.on("open")
    def on_open():
        global DATA_CHANNEL_OPENED
        DATA_CHANNEL_OPENED = True

    handler = partial(data_handler, data_channel=dc)
    pc.add_listener("track", handler)

    pc.addTransceiver("video", direction="recvonly")
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    answer = requests.post(URL, json={"sdp": offer.sdp, "type": offer.type}).json()
    print(answer)
    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
    )
    await asyncio.sleep(1000000000)


if __name__ == "__main__":
    asyncio.run(main())
