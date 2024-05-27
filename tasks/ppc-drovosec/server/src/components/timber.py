from src.components.base import GameComponent


class Timber(GameComponent):
    def __init__(self, move_step: int, *args, **kwargs):
        self.move_step = move_step
        super().__init__(*args, **kwargs)
