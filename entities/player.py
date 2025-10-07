"""
Módulo que define la entidad controlable por el jugador: Pac-Man.
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
        
        # Velocidad ralentizada para jugabilidad cómoda
        self.move_delay = 0
        self.move_frequency = 8  # 7.5 movimientos/segundo a 60fps
        
        # Animación
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 5
        self.is_moving = True

    def lose_life(self) -> bool:
        """Reduce una vida. Retorna True si aún quedan vidas."""
        self.lives -= 1
        print(f"[PACMAN] Vida perdida. Vidas restantes: {self.lives}")
        return self.lives > 0

    def reset_position(self, new_position: Tuple[int, int]) -> None:
        """Reinicia posición tras perder una vida."""
        self.position = list(new_position)
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.animation_frame = 0
        self.move_delay = 0
        print(f"[PACMAN] Posición reiniciada a {new_position}")

    def update_animation(self) -> None:
        """Actualiza el frame de animación (boca abierta/cerrada)."""
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 3

    def get_grid_position(self) -> Tuple[int, int]:
        """Devuelve posición actual en el grid (inmutable)."""
        return tuple(self.position)

    def get_direction_tuple(self) -> Tuple[int, int]:
        """Devuelve el delta de movimiento según la dirección actual."""
        direction_map = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }
        return direction_map.get(self.direction, (0, 0))

    def __repr__(self) -> str:
        """Representación en string para debugging."""
        return (f"PacMan(pos={self.position}, dir={self.direction}, "
                f"lives={self.lives}, score={self.score})")