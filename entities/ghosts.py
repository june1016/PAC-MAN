"""
Sistema de fantasmas con comportamientos distintivos.
Compatible con el sistema de colisiones de board.py y la lógica de game.py.
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
        
        # CORREGIDO: Velocidad base más lenta
        self.speed = 1
        self.move_delay = 0
        self.move_frequency = 8  # Velocidad base (se sobrescribe en subclases)

    def move(self, maze: List[List[int]], target: Tuple[int, int], board_gen) -> None:
        # Actualizar timer de vulnerabilidad
        if self.is_vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.is_vulnerable = False
        
        # Sistema de delay para ralentizar movimiento
        self.move_delay += 1
        if self.move_delay < self.move_frequency:
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


# ==================== FANTASMAS ESPECÍFICOS ====================

class Blinky(Ghost):
    """Fantasma rojo - Perseguidor agresivo."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "blinky")
        # CORREGIDO: Más lento que Pac-Man (6 vs 8)
        self.move_frequency = 8

class Pinky(Ghost):
    """Fantasma rosa - Emboscador."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "pinky")
        self.move_frequency = 9

class Inky(Ghost):
    """Fantasma cyan - Impredecible."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "inky")
        self.move_frequency = 10

class Clyde(Ghost):
    """Fantasma naranja - Tímido."""
    def __init__(self, initial_position: Tuple[int, int]):
        super().__init__(initial_position, "clyde")
        self.move_frequency = 11