from PIL import ImageOps
from PIL.Image import Image

from src.components.base import GameComponent


class PlayerState():
    DEFAULT = 'DEFAULT'
    START_ATTACK = 'START_ATTACK'
    ATTACK = 'ATTACK'


class Player(GameComponent):
    def __init__(self, pos_x: float, pos_y: float, image: Image, attack_images: tuple[Image, Image]):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = image
        self.mirrored = False

        self._attack_steps = {
            PlayerState.START_ATTACK: 6,
            PlayerState.ATTACK: 4,
        }
        self._images = {
            PlayerState.DEFAULT: image,
            PlayerState.START_ATTACK: attack_images[0],
            PlayerState.ATTACK: attack_images[1],
        }
        self._mirrored_images = {
            PlayerState.DEFAULT: ImageOps.mirror(image),
            PlayerState.START_ATTACK: ImageOps.mirror(attack_images[0]),
            PlayerState.ATTACK: ImageOps.mirror(attack_images[1]),
        }
        self._current_attack_step = 0
        self._current_state = PlayerState.DEFAULT

    def process_attack(self, init_attack: bool = False) -> PlayerState:
        if not init_attack and self._current_state == PlayerState.DEFAULT:
            return self._current_state

        if init_attack:
            self._current_state = PlayerState.START_ATTACK
            self._current_attack_step = 0

            self._change_image(self._current_state)
            return self._current_state

        self._current_attack_step += 1
        if self._current_attack_step > self._attack_steps[self._current_state]:
            match self._current_state:
                case PlayerState.START_ATTACK:
                    self._current_state = PlayerState.ATTACK
                case PlayerState.ATTACK:
                    self._current_state = PlayerState.DEFAULT
            self._current_attack_step = 0

        self._change_image(self._current_state)
        return self._current_state

    def mirror(self):
        self.mirrored = not self.mirrored
        self._change_image(self._current_state)

    def _change_image(self, state):
        if self.mirrored:
            self.image = self._mirrored_images[state]
            return

        self.image = self._images[state]
