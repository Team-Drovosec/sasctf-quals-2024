from PIL import ImageFont
from dataclasses import dataclass


@dataclass
class DifficultyConfig:
    START_MOVE_STEP: int
    END_MOVE_STEP: int
    START_SPAWN_DELAY: int
    END_SPAWN_DELAY: int


BACKGROUND_PATH_IMAGE = "sprites/bg.png"
BACKGROUND_WIDTH = 1280

TIMBER_PATH_IMAGE = "sprites/timber.png"
TIMBER_HEIGHT = 38

BEAVER_IMAGE_PATHS = ["sprites/beaver-1.png", "sprites/beaver-2.png"]

HEART_PATH_IMAGE = "sprites/heart.png"
HEARTH_WIDTH = 30

PLAYER_PATH_IMAGE = "sprites/player.png"
PLAYER_WIDTH = 100

PLAYER_START_ATTACK_PATH_IMAGE = "sprites/player-attack-1.png"

PLAYER_ATTACK_IMAGE = "sprites/player-attack-2.png"

PLAYER_POSITIONS = {
    ('w', 'a'): (546, 295),
    ('w', 'd'): (677, 295),
    ('s', 'a'): (546, 459),
    ('s', 'd'): (677, 459),
}

SCORE_FONT = ImageFont.truetype("fonts/roboto.ttf", 52)
TEXT_FONT = ImageFont.truetype("fonts/roboto.ttf", 80)
FLAG_FONT = ImageFont.truetype("fonts/roboto.ttf", 50)

LEFT_TIMBER_POSITION_LOSE = 617
RIGHT_TIMBER_POSITION_LOSE = 707

COST_KILLING_BEAVER = -10

DIFFICULTY_LEVELS = {  # TODO: Add more levels in production
    0: DifficultyConfig(
        START_MOVE_STEP=7,
        END_MOVE_STEP=7,
        START_SPAWN_DELAY=75,
        END_SPAWN_DELAY=75,
    ),
}

WINNING_SCORE = 160

FLAG = "flag"