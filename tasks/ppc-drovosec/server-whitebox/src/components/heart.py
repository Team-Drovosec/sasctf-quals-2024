from PIL.Image import Image

from src.components.base import GameComponent


class Heart(GameComponent):
    def __init__(self, pos_x: int, pos_y: int, image: Image):
        super().__init__(pos_x, pos_y, image)
        self._opacity_image = image.copy()
        self.opacity = 1

    def draw(self, base: Image):
        self._opacity_image.putalpha(int(self.opacity * 255))
        self.pos_y -= round(self.opacity * 4)
        self.image.paste(self._opacity_image, mask=self.image)
        super().draw(base)
