from PIL.Image import Image
from PIL import ImageOps


class GameComponent:
    def __init__(self, pos_x: int, pos_y: int, image: Image):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = image
        self.mirrored = False
        self._original_image = image
        self._mirrored_image = ImageOps.mirror(image)

    def draw(self, base: Image):
        base.paste(self.image, box=(self.pos_x, self.pos_y), mask=self.image)

    def change_pos(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

    def mirror(self):
        self.mirrored = not self.mirrored
        if self.mirrored:
            self.image = self._mirrored_image
            return
        self.image = self._original_image
