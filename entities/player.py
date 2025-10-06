"""
Módulo que define la entidad controlable por el jugador: Pac-Man.
La clase PacMan gestiona su posición, dirección, vidas y puntaje.
El movimiento real y las colisiones se manejan en GameCore.
"""
from typing import Tuple

class PacMan:
    """Representa al jugador en el juego PACMAN."""

    def __init__(self, initial_position: Tuple[int, int], lives: int = 3):
        self.position = list(initial_position)
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.lives = lives
        self.score = 0
        
        # CORREGIDO: Velocidad más lenta para gameplay clásico
        self.move_delay = 0
        self.move_frequency = 6  # Antes: 4 | Ahora: 6 (10 mov/seg)
        
        # Animación
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 5
        self.is_moving = True

    def lose_life(self) -> bool:
        self.lives -= 1
        print(f"[PACMAN] Vida perdida. Vidas restantes: {self.lives}")
        return self.lives > 0

    def reset_position(self, new_position: Tuple[int, int]) -> None:
        self.position = list(new_position)
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.animation_frame = 0
        print(f"[PACMAN] Posición reiniciada a {new_position}")

    def update_animation(self) -> None:
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 3

    def get_grid_position(self) -> Tuple[int, int]:
        return tuple(self.position)

    def get_direction_tuple(self) -> Tuple[int, int]:
        direction_map = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }
        return direction_map.get(self.direction, (0, 0))

    def __repr__(self) -> str:
        return (f"PacMan(pos={self.position}, dir={self.direction}, "
                f"lives={self.lives}, score={self.score})")
