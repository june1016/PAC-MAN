# entities/ghosts.py
"""
Sistema de fantasmas con comportamientos distintivos y estados.
Implementa movimiento, persecución, huida y sistema de casa.
"""

import random
import math
from typing import List, Tuple, Optional


# Estados de los fantasmas
class GhostState:
    IN_HOUSE = "IN_HOUSE"           # Dentro de la casa
    LEAVING_HOUSE = "LEAVING_HOUSE" # Saliendo de la casa
    CHASE = "CHASE"                 # Persiguiendo a Pac-Man
    SCATTER = "SCATTER"             # Modo disperso
    FRIGHTENED = "FRIGHTENED"       # Vulnerable (comible)
    EATEN = "EATEN"                 # Comido, regresando a casa


class Ghost:
    """Clase base para todos los fantasmas con sistema de estados."""

    def __init__(self, initial_position: tuple[int, int], ghost_type: str = "blinky"):
        self.position = list(initial_position)
        self.float_pos = [float(self.position[0]), float(self.position[1])]
        
        # Sistema de movimiento
        self.move_counter = random.randint(0, 15)  # Randomizar inicio para evitar sincronización
        self.speed = 0.08
        self.last_direction = (0, 0)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
        
        # Estado y vulnerabilidad
        self.state = GhostState.IN_HOUSE
        self.ghost_type = ghost_type
        self.is_vulnerable = False
        self.vulnerable_timer = 0
        self.release_timer = 0  # Tiempo antes de salir de la casa
        
        # Configurar tiempos de liberación por tipo
        release_times = {"blinky": 0, "pinky": 60, "inky": 120, "clyde": 180}
        self.release_timer = release_times.get(ghost_type, 0)

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, 
             pacman_direction: Optional[str] = None) -> None:
        """Movimiento principal con manejo de estados."""
        self.move_counter += 1
        if self.move_counter < 15:  # Moverse cada 15 frames
            self.interpolate_position()
            return
        self.move_counter = 0

        # Actualizar estado de vulnerabilidad
        if self.is_vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.is_vulnerable = False
                self.state = GhostState.CHASE

        # Manejo de estados
        if self.state == GhostState.IN_HOUSE:
            self._handle_in_house(maze)
        elif self.state == GhostState.LEAVING_HOUSE:
            self._handle_leaving_house(maze)
        elif self.state == GhostState.FRIGHTENED:
            self._handle_frightened(maze)
        elif self.state == GhostState.EATEN:
            self._handle_eaten(maze)
        else:  # CHASE o SCATTER
            self._handle_active_movement(maze, pacman_position, pacman_direction)

        self.interpolate_position()

    def _handle_in_house(self, maze: List[List[int]]) -> None:
        """Comportamiento dentro de la casa (esperar y oscilar)."""
        self.release_timer -= 1
        if self.release_timer <= 0:
            self.state = GhostState.LEAVING_HOUSE
        else:
            # Oscilar verticalmente en la casa
            if random.random() < 0.3:
                new_row = self.position[0] + random.choice([-1, 1])
                new_col = self.position[1]
                if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                    # Permitir movimiento en la casa (tiles 0 o 2)
                    if maze[new_row][new_col] in [0, 2]:
                        self.position = [new_row, new_col]

    def _handle_leaving_house(self, maze: List[List[int]]) -> None:
        """Salir de la casa hacia la posición de salida."""
        exit_position = (8, 10)  # GHOST_HOUSE_EXIT del board.py
        
        # Moverse hacia la salida
        if self.position[0] > exit_position[0]:
            new_row = self.position[0] - 1
            new_col = self.position[1]
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                if maze[new_row][new_col] in [0, 2]:
                    self.position = [new_row, new_col]
                    self.last_direction = (-1, 0)
        elif abs(self.position[1] - exit_position[1]) > 0:
            # Centrar horizontalmente
            new_row = self.position[0]
            new_col = self.position[1] + (1 if self.position[1] < exit_position[1] else -1)
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                if maze[new_row][new_col] in [0, 2]:
                    self.position = [new_row, new_col]
        else:
            # Ya salió, cambiar a modo persecución
            self.state = GhostState.CHASE

    def _handle_frightened(self, maze: List[List[int]]) -> None:
        """Movimiento aleatorio cuando está vulnerable."""
        valid_moves = self._get_valid_moves(maze)
        next_pos = self._choose_random_move(valid_moves)
        if next_pos:
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = list(next_pos)

    def _handle_eaten(self, maze: List[List[int]]) -> None:
        """Regresar a la casa después de ser comido."""
        house_center = (10, 10)
        next_pos = self._move_towards_target(maze, house_center, allow_house=True)
        if next_pos:
            self.position = list(next_pos)
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            
            # Si llegó a la casa, reiniciar
            if tuple(self.position) == house_center:
                self.state = GhostState.IN_HOUSE
                self.release_timer = 120  # Tiempo antes de volver a salir

    def _handle_active_movement(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]], 
                                 pacman_direction: Optional[str]) -> None:
        """Implementado por subclases - movimiento específico de cada fantasma."""
        raise NotImplementedError("Subclasses must implement _handle_active_movement()")

    def interpolate_position(self):
        """Interpola suavemente hacia la posición objetivo."""
        target_x = float(self.position[0])
        target_y = float(self.position[1])
        
        if abs(self.float_pos[0] - target_x) > self.speed:
            self.float_pos[0] += self.speed if self.float_pos[0] < target_x else -self.speed
        else:
            self.float_pos[0] = target_x

        if abs(self.float_pos[1] - target_y) > self.speed:
            self.float_pos[1] += self.speed if self.float_pos[1] < target_y else -self.speed
        else:
            self.float_pos[1] = target_y

    def _get_valid_moves(self, maze: List[List[int]], allow_house: bool = False) -> List[tuple[int, int]]:
        """Obtiene movimientos válidos evitando U-turn."""
        current_row, current_col = self.position
        valid_moves = []
        
        for dr, dc in self.directions:
            new_row, new_col = current_row + dr, current_col + dc
            
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                cell_value = maze[new_row][new_col]
                # Permitir movimiento en PATH (0) y opcionalmente en GHOST_HOUSE (2)
                if cell_value == 0 or (allow_house and cell_value == 2):
                    # Evitar U-turn
                    if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                        valid_moves.append((new_row, new_col))
        
        return valid_moves

    def _choose_random_move(self, valid_moves: List[tuple[int, int]]) -> Optional[tuple[int, int]]:
        """Elige un movimiento aleatorio."""
        return random.choice(valid_moves) if valid_moves else None

    def _move_towards_target(self, maze: List[List[int]], target: tuple[int, int], 
                             allow_house: bool = False) -> Optional[tuple[int, int]]:
        """Moverse hacia un objetivo usando distancia Manhattan."""
        current_row, current_col = self.position
        best_move = None
        best_distance = float('inf')

        for dr, dc in self.directions:
            new_row, new_col = current_row + dr, current_col + dc
            
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                cell_value = maze[new_row][new_col]
                if cell_value == 0 or (allow_house and cell_value == 2):
                    # Evitar U-turn
                    if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                        dist = abs(new_row - target[0]) + abs(new_col - target[1])
                        if dist < best_distance:
                            best_distance = dist
                            best_move = (new_row, new_col)

        return best_move

    def make_vulnerable(self, duration: int = 300):
        """Activa el estado vulnerable (frightened)."""
        self.is_vulnerable = True
        self.vulnerable_timer = duration
        self.state = GhostState.FRIGHTENED

    def eat_ghost(self):
        """Marca el fantasma como comido."""
        self.is_vulnerable = False
        self.vulnerable_timer = 0
        self.state = GhostState.EATEN


class Blinky(Ghost):
    """Fantasma rojo - Persigue directamente a Pac-Man."""
    
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "blinky")

    def _handle_active_movement(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]], 
                                 pacman_direction: Optional[str]) -> None:
        if not pacman_position:
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            next_pos = self._move_towards_target(maze, pacman_position)

        if next_pos:
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = list(next_pos)


class Pinky(Ghost):
    """Fantasma rosa - Embosca 4 pasos adelante de Pac-Man."""
    
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "pinky")

    def _handle_active_movement(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]], 
                                 pacman_direction: Optional[str]) -> None:
        if not pacman_position or not pacman_direction:
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            # Calcular objetivo 4 pasos adelante
            target_offset = {"UP": (-4, 0), "DOWN": (4, 0), "LEFT": (0, -4), "RIGHT": (0, 4)}
            offset = target_offset.get(pacman_direction, (0, 0))
            target = (pacman_position[0] + offset[0], pacman_position[1] + offset[1])
            
            # Clamp al tablero
            rows, cols = len(maze), len(maze[0])
            target = (max(0, min(rows - 1, target[0])), max(0, min(cols - 1, target[1])))
            next_pos = self._move_towards_target(maze, target)

        if next_pos:
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = list(next_pos)


class Inky(Ghost):
    """Fantasma cyan - Comportamiento impredecible (patrulla)."""
    
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "inky")

    def _handle_active_movement(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]], 
                                 pacman_direction: Optional[str]) -> None:
        if not pacman_position:
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            dist = math.sqrt((self.position[0] - pacman_position[0])**2 + 
                           (self.position[1] - pacman_position[1])**2)
            
            if dist < 5:  # Cerca: alejarse
                dx = self.position[0] - pacman_position[0]
                dy = self.position[1] - pacman_position[1]
                target = (self.position[0] + int(dx), self.position[1] + int(dy))
                rows, cols = len(maze), len(maze[0])
                target = (max(0, min(rows - 1, target[0])), max(0, min(cols - 1, target[1])))
                next_pos = self._move_towards_target(maze, target)
            else:  # Lejos: moverse aleatoriamente
                valid_moves = self._get_valid_moves(maze)
                next_pos = self._choose_random_move(valid_moves)

        if next_pos:
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = list(next_pos)


class Clyde(Ghost):
    """Fantasma naranja - Huye si está cerca, persigue si está lejos."""
    
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "clyde")

    def _handle_active_movement(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]], 
                                 pacman_direction: Optional[str]) -> None:
        if not pacman_position:
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            dist = math.sqrt((self.position[0] - pacman_position[0])**2 + 
                           (self.position[1] - pacman_position[1])**2)
            
            if dist < 8:  # Cerca: huir
                dx = self.position[0] - pacman_position[0]
                dy = self.position[1] - pacman_position[1]
                target = (self.position[0] + int(dx * 2), self.position[1] + int(dy * 2))
                rows, cols = len(maze), len(maze[0])
                target = (max(0, min(rows - 1, target[0])), max(0, min(cols - 1, target[1])))
                next_pos = self._move_towards_target(maze, target)
            else:  # Lejos: perseguir
                next_pos = self._move_towards_target(maze, pacman_position)

        if next_pos:
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = list(next_pos)