"""
Sistema de fantasmas con comportamientos distintivos.
Velocidades calibradas para jugabilidad cómoda.
"""
import random
from typing import List, Tuple, Optional


class Ghost:
    """Clase base para todos los fantasmas."""

    def __init__(self, initial_position: Tuple[int, int], ghost_type: str = "blinky"):
        self.position = list(initial_position)
        self.last_direction = (0, 0)
        self.ghost_type = ghost_type
        self.in_house = True
        self.is_vulnerable = False
        self.vulnerable_timer = 0
        
        self.speed = 1
        self.move_delay = 0
        self.move_frequency = 8

    def move(self, maze: List[List[int]], target: Tuple[int, int], board_gen) -> None:
        if self.is_vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.is_vulnerable = False
        
        self.move_delay += 1
        current_frequency = self.move_frequency
        if self.is_vulnerable:
            current_frequency = int(self.move_frequency * 1.5)
        
        if self.move_delay < current_frequency:
            return
        
        self.move_delay = 0
        next_pos = self._get_best_move(target, board_gen)
        
        if next_pos:
            self.last_direction = (
                next_pos[0] - self.position[0],
                next_pos[1] - self.position[1]
            )
            self.position = list(next_pos)

    def _get_best_move(self, target: Tuple[int, int], board_gen) -> Optional[Tuple[int, int]]:
        current_row, current_col = self.position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        best_move = None
        best_distance = float('inf')
        
        for dr, dc in directions:
            new_row = current_row + dr
            new_col = current_col + dc
            
            if not board_gen.can_ghost_move_to(new_row, new_col):
                continue
            
            if (dr, dc) == (-self.last_direction[0], -self.last_direction[1]):
                continue
            
            distance = abs(new_row - target[0]) + abs(new_col - target[1])
            
            if distance < best_distance:
                best_distance = distance
                best_move = (new_row, new_col)
        
        if best_move is None:
            for dr, dc in directions:
                new_row = current_row + dr
                new_col = current_col + dc
                
                if board_gen.can_ghost_move_to(new_row, new_col):
                    return (new_row, new_col)
        
        return best_move

    def __repr__(self) -> str:
        return (f"{self.ghost_type.capitalize()}(pos={self.position}, "
                f"in_house={self.in_house}, vulnerable={self.is_vulnerable})")


class Blinky(Ghost):
    """Fantasma ROJO - El más agresivo."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "blinky")
        self.move_frequency = 12


class Pinky(Ghost):
    """Fantasma ROSA - Emboscador."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "pinky")
        self.move_frequency = 14


class Inky(Ghost):
    """Fantasma CYAN - Impredecible."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "inky")
        self.move_frequency = 14


class Clyde(Ghost):
    """Fantasma NARANJA - Tímido."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "clyde")
        self.move_frequency = 16