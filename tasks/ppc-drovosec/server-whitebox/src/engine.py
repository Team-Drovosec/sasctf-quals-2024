import random
from collections import defaultdict
from enum import Enum, IntEnum

from PIL import Image, ImageDraw, ImageOps

from src.components.base import GameComponent
from src.components.beaver import Beaver
from src.components.heart import Heart
from src.components.player import Player, PlayerState
from src.components.timber import Timber
from src.config import (BACKGROUND_PATH_IMAGE, BACKGROUND_WIDTH, BEAVER_IMAGE_PATHS, COST_KILLING_BEAVER,
                        HEART_PATH_IMAGE,
                        LEFT_TIMBER_POSITION_LOSE,
                        PLAYER_ATTACK_IMAGE,
                        PLAYER_PATH_IMAGE,
                        PLAYER_POSITIONS, PLAYER_START_ATTACK_PATH_IMAGE, PLAYER_WIDTH, RIGHT_TIMBER_POSITION_LOSE,
                        SCORE_FONT, TEXT_FONT, TIMBER_PATH_IMAGE,
                        TIMBER_HEIGHT, DIFFICULTY_LEVELS, WINNING_SCORE, FLAG, FLAG_FONT)
from src.utils import resize_image


class GameComponentsPosition(tuple, Enum):
    LEFT_UP = ('w', 'a')
    RIGHT_UP = ('w', 'd')
    LEFT_DOWN = ('s', 'a')
    RIGHT_DOWN = ('s', 'd')


class Sides(IntEnum):
    LEFT = 0
    RIGHT = 1


class HeartManager:
    def __init__(self):
        self.heart_image = resize_image(Image.open(HEART_PATH_IMAGE), new_height=TIMBER_HEIGHT)
        self.heart_positions = {
            GameComponentsPosition.LEFT_UP: (LEFT_TIMBER_POSITION_LOSE, 374),
            GameComponentsPosition.RIGHT_UP: (RIGHT_TIMBER_POSITION_LOSE - self.heart_image.width, 374),
            GameComponentsPosition.LEFT_DOWN: (LEFT_TIMBER_POSITION_LOSE, 540),
            GameComponentsPosition.RIGHT_DOWN: (RIGHT_TIMBER_POSITION_LOSE  - self.heart_image.width, 540),
        }
        self.heart_images = {
            GameComponentsPosition.LEFT_UP: self.heart_image.copy(),
            GameComponentsPosition.RIGHT_UP: self.heart_image.copy(),
            GameComponentsPosition.LEFT_DOWN: self.heart_image.copy(),
            GameComponentsPosition.RIGHT_DOWN: self.heart_image.copy(),
        }
        self.active_hearts = {}

    def spawn(self, position: GameComponentsPosition) -> None:
        pos_x, pos_y = self.heart_positions[position][0], self.heart_positions[position][1]
        self.active_hearts[position] = Heart(pos_x, pos_y, self.heart_images[position])

    def move_and_draw(self, base: Image) -> None:
        heart_keys_to_delete = []
        for key, heart in self.active_hearts.items():
            heart.opacity -= 0.1
            if heart.opacity <= 0:
                heart_keys_to_delete.append(key)
                continue
            heart.draw(base)
        for key in heart_keys_to_delete:
            del self.active_hearts[key]


class ComponentsManager:
    def __init__(self):
        self.hearth_manager = HeartManager()
        timber_image = resize_image(Image.open(TIMBER_PATH_IMAGE), new_height=TIMBER_HEIGHT)
        self.timber_images = {
            GameComponentsPosition.LEFT_UP: timber_image.copy(),
            GameComponentsPosition.RIGHT_UP: ImageOps.mirror(timber_image),
            GameComponentsPosition.LEFT_DOWN: timber_image.copy(),
            GameComponentsPosition.RIGHT_DOWN: ImageOps.mirror(timber_image),
        }
        self.component_positions = {
            GameComponentsPosition.LEFT_UP: (0, 374),
            GameComponentsPosition.RIGHT_UP: (BACKGROUND_WIDTH - timber_image.width, 374),
            GameComponentsPosition.LEFT_DOWN: (0, 540),
            GameComponentsPosition.RIGHT_DOWN: (BACKGROUND_WIDTH - timber_image.width, 540),
        }

        beaver_image = [
            resize_image(Image.open(image_path), new_height=TIMBER_HEIGHT)
            for image_path in BEAVER_IMAGE_PATHS
        ]
        self.beaver_images = {
            Sides.LEFT: beaver_image,
            Sides.RIGHT: list(map(lambda img: ImageOps.mirror(img), beaver_image)),
        }

        self.lost_components = set()
        self.active_components: dict[GameComponentsPosition, list[Beaver | Timber]] = defaultdict(list)
        self.move_step = DIFFICULTY_LEVELS[0].START_MOVE_STEP

    def spawn(self):
        available_positions = [
            GameComponentsPosition.LEFT_UP,
            GameComponentsPosition.RIGHT_UP,
            GameComponentsPosition.LEFT_DOWN,
            GameComponentsPosition.RIGHT_DOWN,
        ]

        position_to_spawn = random.choice(available_positions)

        if random.random() < 0.75:
            self.active_components[position_to_spawn].append(
                Timber(
                    pos_x=self.component_positions[position_to_spawn][0],
                    pos_y=self.component_positions[position_to_spawn][1],
                    image=self.timber_images[position_to_spawn],
                    move_step=self.move_step,
                ),
            )
        else:
            pos_x = self.component_positions[position_to_spawn][0]
            pos_y = self.component_positions[position_to_spawn][1]

            if position_to_spawn in (GameComponentsPosition.LEFT_UP, GameComponentsPosition.LEFT_DOWN):
                images = self.beaver_images[Sides.LEFT]
            else:
                images = self.beaver_images[Sides.RIGHT]

            self.active_components[position_to_spawn].append(
                Beaver(
                    pos_x=pos_x,
                    pos_y=pos_y,
                    images=images,
                    move_step=self.move_step,
                ),
            )

    def move_and_draw(self, base: Image):
        self._update_lost_components()
        for i, components in self.active_components.items():
            for component in components:
                if i in (GameComponentsPosition.LEFT_UP, GameComponentsPosition.LEFT_DOWN):
                    if component in self.lost_components:
                        component.pos_x = LEFT_TIMBER_POSITION_LOSE
                        component.pos_y += 1
                    else:
                        component.pos_x += component.move_step
                else:
                    if component in self.lost_components:
                        component.pos_x = RIGHT_TIMBER_POSITION_LOSE - component.image.width
                        component.pos_y += 1
                    else:
                        component.pos_x -= component.move_step
                if isinstance(component, Beaver):
                    component.next_state()
                component.draw(base)
        self.hearth_manager.move_and_draw(base)

    def is_lose(self) -> bool:
        return bool(self.lost_components)

    def get_lower_lost_timber_y_position(self) -> int:
        return max([timber.pos_y for timber in self.lost_components])

    def _update_lost_components(self) -> None:
        lost_timbers = set()
        component_positions_to_delete: list[tuple[GameComponentsPosition, int]] = []
        for position, components in self.active_components.items():
            for ind, component in enumerate(components):
                if position in (GameComponentsPosition.LEFT_UP, GameComponentsPosition.LEFT_DOWN):
                    next_pos_x = component.pos_x + self.move_step
                    if next_pos_x > LEFT_TIMBER_POSITION_LOSE:
                        if isinstance(component, Beaver):
                            component_positions_to_delete.append((position, ind))
                            continue
                        lost_timbers.add(component)
                else:
                    next_pos_x = component.pos_x - self.move_step
                    if next_pos_x + component.image.width < RIGHT_TIMBER_POSITION_LOSE:
                        if isinstance(component, Beaver):
                            component_positions_to_delete.append((position, ind))
                            continue
                        lost_timbers.add(component)
        self.lost_components = self.lost_components | lost_timbers
        for component_position, ind in component_positions_to_delete:
            self.hearth_manager.spawn(component_position)
            self.active_components[component_position].pop(ind)



class GameEngine:
    def __init__(self):
        self.scene = Image.open(BACKGROUND_PATH_IMAGE)
        self.scene = resize_image(self.scene, new_width=BACKGROUND_WIDTH)

        self.spawn_delay = DIFFICULTY_LEVELS[0].START_SPAWN_DELAY
        self.current_tick = 0

        self.score = 0
        self.black_screen_opacity = 0.2

        self.components_manager = ComponentsManager()

        player_image = resize_image(Image.open(PLAYER_PATH_IMAGE), new_width=PLAYER_WIDTH)
        start_attack_image = resize_image(Image.open(PLAYER_START_ATTACK_PATH_IMAGE), new_width=PLAYER_WIDTH)
        attack_image = resize_image(Image.open(PLAYER_ATTACK_IMAGE), new_width=PLAYER_WIDTH)

        start_position = list(PLAYER_POSITIONS.values())[0]
        self.player = Player(pos_x=start_position[0], pos_y=start_position[1], image=player_image, attack_images=(start_attack_image, attack_image))
        self.player_position = GameComponentsPosition.LEFT_UP

        self.is_lose = False

    def next_step(self, pressed_keys: list[str]) -> Image:
        if not self.is_lose and not self.is_win:
            if self.current_tick >= self.spawn_delay:
                self.components_manager.spawn()
                self.current_tick = 0

            self.current_tick += 1
            self.process_keys(pressed_keys)

            player_state = self.player.process_attack()
            self._check_attack(player_state)

        current_scene = self._get_current_scene()
        if self.is_win:
            self._draw_win_screen(current_scene)
        elif self.is_lose:
            self._draw_lose_screen(current_scene)

        self.change_game_speed()

        return current_scene

    def change_game_speed(self):
        pass  # TODO: Fix this in the production version!

    def process_keys(self, pressed_keys) -> None:
        for key in pressed_keys:
            new_position = None
            match key.lower():
                case 'w':
                    new_position = ('w', self.player_position[1])
                case 's':
                    new_position = ('s', self.player_position[1])
                case 'a':
                    if self.player.mirrored:
                        self.player.mirror()
                    new_position = (self.player_position[0], 'a')
                case 'd':
                    if not self.player.mirrored:
                        self.player.mirror()
                    new_position = (self.player_position[0], 'd')
                case "attack":
                    self.player.process_attack(init_attack=True)
            if new_position:
                self.player_position = new_position
                self.player.pos_x, self.player.pos_y = PLAYER_POSITIONS[new_position]

    def _get_current_scene(self) -> Image:
        current_scene = self.scene.copy()

        self.player.draw(current_scene)

        self.components_manager.move_and_draw(current_scene)

        if self.components_manager.is_lose() or self.score < 0:
            self.is_lose = True

        draw = ImageDraw.Draw(current_scene)
        draw.text(
            (current_scene.width // 2, 0),
            str(self.score),
            (255, 255, 255),
            font=SCORE_FONT,
            stroke_width=3,
            stroke_fill=(0, 0, 0)
        )

        return current_scene

    def _check_attack(self, player_state: PlayerState) -> bool:
        if player_state != PlayerState.ATTACK:
            return False

        closed_component = self.components_manager.active_components.get(self.player_position)
        if not closed_component:
            return False
        closed_component = closed_component[0]

        if closed_component and self.__process_attack_on_component(closed_component):
            if isinstance(closed_component, Beaver):
                self.score += COST_KILLING_BEAVER
            else:
                self.score += 1

            self.components_manager.active_components[self.player_position].pop(0)

    def _draw_lose_screen(self, current_scene: Image) -> None:
        game_over_text = "GAME OVER"
        self._draw_black_screen(current_scene, game_over_text)

    def _draw_win_screen(self, current_scene: Image) -> None:
        self._draw_black_screen(current_scene, FLAG, font=FLAG_FONT)

    def _draw_black_screen(self, current_scene: Image, text: str, font=TEXT_FONT) -> None:
        draw = ImageDraw.Draw(current_scene, "RGBA")
        draw.rectangle(((0, 0), (current_scene.width, current_scene.height)),
                       fill=(0, 0, 0, int(self.black_screen_opacity * 255)))
        _, _, w, h = draw.textbbox((0, 0), text, font=font)
        draw.text(
            ((current_scene.width - w) // 2, (current_scene.height - h) // 2),
            text,
            (255, 255, 255, 0),
            font=font,
        )

        self.black_screen_opacity = min(self.black_screen_opacity + 0.01, 1)

    def __process_attack_on_component(self, component: GameComponent) -> bool:
        if self.player.pos_x < component.pos_x + component.image.width // 2 < self.player.pos_x + self.player.image.width:
            return True
        return False

    @property
    def is_win(self) -> bool:
        return self.score >= WINNING_SCORE

    @property
    def is_game_over(self) -> bool:
        if not self.is_lose:
            return False
        return self.black_screen_opacity >= 1
