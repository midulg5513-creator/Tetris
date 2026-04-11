from __future__ import annotations

from dataclasses import dataclass
import random

from .pieces import BOMB_INDEX, Tetromino


GRID_WIDTH = 10
GRID_HEIGHT = 20

MOVE_ACTIONS = {
    "left": (-1, 0),
    "right": (1, 0),
    "down": (0, 1),
}

GridCell = tuple[int, int, int] | None


@dataclass(slots=True)
class RepeatTracker:
    held: bool = False
    elapsed: float = 0.0
    repeating: bool = False


class GameState:
    def __init__(self, random_source: random.Random | None = None) -> None:
        self._random = random_source if random_source is not None else random.Random()
        self.key_delay = 0.15
        self.key_interval = 0.05
        self.repeat_trackers = {action: RepeatTracker() for action in MOVE_ACTIONS}
        self.reset()

    def reset(self) -> None:
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self._spawn_piece()
        self.next_piece = self._spawn_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.fall_time = 0.0
        self.paused = False
        self.explosion_active = False
        self.explosion_time = 0.0
        self.explosion_positions: list[tuple[int, int]] = []

        for tracker in self.repeat_trackers.values():
            tracker.held = False
            tracker.elapsed = 0.0
            tracker.repeating = False

    def _spawn_piece(self) -> Tetromino:
        return Tetromino.spawn(GRID_WIDTH, self._random)

    def new_piece(self) -> None:
        self.current_piece = self.next_piece
        self.next_piece = self._spawn_piece()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def check_collision(
        self,
        piece: Tetromino,
        dx: int = 0,
        dy: int = 0,
        shape: list[list[int]] | None = None,
    ) -> bool:
        candidate_shape = piece.shape if shape is None else shape
        for row_index, row in enumerate(candidate_shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                new_x = piece.x + col_index + dx
                new_y = piece.y + row_index + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return True
                if new_y >= 0 and self.grid[new_y][new_x]:
                    return True
        return False

    def move_current(self, dx: int, dy: int) -> bool:
        if self.check_collision(self.current_piece, dx, dy):
            return False

        self.current_piece.x += dx
        self.current_piece.y += dy
        return True

    def rotate_current(self) -> None:
        if self.current_piece.shape_index == BOMB_INDEX:
            return

        rotated_shape = self.current_piece.rotated_shape()
        if rotated_shape is None:
            return

        if not self.check_collision(self.current_piece, shape=rotated_shape):
            self.current_piece.shape = rotated_shape
            return

        for wall_kick in (-1, 1):
            if not self.check_collision(self.current_piece, dx=wall_kick, shape=rotated_shape):
                self.current_piece.x += wall_kick
                self.current_piece.shape = rotated_shape
                return

    def explode_bomb(self, x: int, y: int) -> None:
        self.explosion_positions = []
        for offset_x in (-1, 0, 1):
            for offset_y in (-1, 0, 1):
                if offset_x == 0 and offset_y == 0:
                    continue

                grid_x = x + offset_x
                grid_y = y + offset_y
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    self.grid[grid_y][grid_x] = None
                    self.explosion_positions.append((grid_x, grid_y))

        self.explosion_active = True
        self.explosion_time = 0.0

    def lock_piece(self) -> None:
        if self.current_piece.shape_index == BOMB_INDEX:
            self.explode_bomb(self.current_piece.x, self.current_piece.y)
            self.new_piece()
            return

        for row_index, row in enumerate(self.current_piece.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue
                target_y = self.current_piece.y + row_index
                if target_y >= 0:
                    self.grid[target_y][self.current_piece.x + col_index] = self.current_piece.color

        self.clear_lines()
        self.new_piece()

    def clear_lines(self) -> None:
        lines_to_clear = [row_index for row_index, row in enumerate(self.grid) if all(row)]
        for row_index in reversed(lines_to_clear):
            del self.grid[row_index]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        if not lines_to_clear:
            return

        self.lines_cleared += len(lines_to_clear)
        self.score += (1, 2, 5, 10)[min(len(lines_to_clear) - 1, 3)] * 100 * self.level
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(0.05, 0.5 - ((self.level - 1) * 0.05))

    def hard_drop(self) -> None:
        while self.move_current(0, 1):
            pass
        self.lock_piece()

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def set_hold(self, action: str, is_pressed: bool) -> None:
        tracker = self.repeat_trackers.get(action)
        if tracker is None:
            return

        tracker.held = is_pressed
        tracker.elapsed = 0.0
        tracker.repeating = False

    def _process_held_action(self, action: str, dt: float) -> None:
        tracker = self.repeat_trackers[action]
        if not tracker.held:
            return

        tracker.elapsed += dt
        threshold = self.key_interval if tracker.repeating else self.key_delay
        if tracker.elapsed < threshold:
            return

        dx, dy = MOVE_ACTIONS[action]
        self.move_current(dx, dy)
        tracker.elapsed = 0.0
        tracker.repeating = True

    def update(self, dt: float) -> None:
        if self.game_over or self.paused:
            return

        if self.explosion_active:
            self.explosion_time += dt
            if self.explosion_time >= 0.5:
                self.explosion_active = False

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0.0
            if not self.move_current(0, 1):
                self.lock_piece()

        for action in MOVE_ACTIONS:
            self._process_held_action(action, dt)
