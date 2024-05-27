import numpy as np
from aiortc import RTCDataChannel, RTCPeerConnection, VideoStreamTrack
from av.video.frame import VideoFrame

from src.engine import GameEngine
from src.utils import close_connection


class GameTrack(VideoStreamTrack):
    kind = "video"

    def __init__(self, pc: RTCPeerConnection):
        super().__init__()
        self.pts = 0
        self.time_base = "1/60"
        self.game_engine = GameEngine()
        self.pressed_keys = []
        self.channel: RTCDataChannel = None
        self.pc = pc

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        scene = self.game_engine.next_step(self.pressed_keys)

        self.pressed_keys = []
        new_frame = VideoFrame.from_ndarray(np.array(scene), format="rgb24")
        new_frame.pts = pts

        if self.game_engine.is_win:
            self.channel.send("game_win")

        if not self.game_engine.is_win and self.game_engine.is_lose:
            self.channel.send("game_over")

        if self.game_engine.is_game_over:
            self.stop()
            await close_connection(self.pc)

        new_frame.time_base = time_base
        return new_frame

    def init_channel(self, channel):
        self.channel = channel
