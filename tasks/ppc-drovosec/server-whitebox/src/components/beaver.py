from PIL.Image import Image

from src.components.base import GameComponent


class Beaver(GameComponent):
    def __init__(self, pos_x: int, pos_y: int, images: list[Image], move_step: int):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = images[0]
        self._images = images
        self._current_state = 0
        self._animation_tick = 0
        self._animation_delay = 3
        self.move_step = move_step

    def next_state(self):
        self._animation_tick += 1
        if self._animation_tick >= self._animation_delay:
            self._current_state = (self._current_state + 1) % len(self._images)
            self._animation_tick = 0
            self.image = self._images[self._current_state]
