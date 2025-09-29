"""
Módulo que define los enemigos del juego: los fantasmas.

Se implementan tipos específicos con comportamientos distintivos.
"""

import random
import math
from typing import List, Tuple, Optional


class Ghost:
    """
    Clase base para todos los fantasmas.
    
    Define la posición y la interfaz común para el movimiento.
    """

    def __init__(self, initial_position: tuple[int, int], ghost_type: str = "blinky"):
        """
        Inicializa al fantasma en una posición dada.
        
        Args:
            initial_position (tuple[int, int]): Posición inicial (fila, columna).
            ghost_type (str): Tipo de fantasma ('blinky', 'pinky', 'inky', 'clyde').
        """
        self.position = list(initial_position)  # [fila, columna] (enteros)
        self.float_pos = [float(self.position[0]), float(self.position[1])]  # [fila, columna] (flotantes)
        self.move_counter = 0  # Contador para limitar movimiento
        self.animation_counter = 0  # Contador para animación (no se usa para fantasmas con un sprite)
        self.animation_frame = 0  # Frame actual de la animación (no se usa para fantasmas con un sprite)
        self.speed = 0.03  # Velocidad de movimiento (ajusta según sea necesario)
        self.last_direction = (0, 0)  # Última dirección de movimiento
        # Direcciones posibles
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
        self.is_vulnerable = False # Estado de vulnerabilidad (cuando PacMan come una moneda grande)
        self.vulnerable_timer = 0 # Contador para el tiempo de vulnerabilidad
        self.ghost_type = ghost_type # Tipo de fantasma
        self.frightened_timer = 0 # Contador para el tiempo de miedo (cuando está vulnerable)

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, pacman_direction: Optional[str] = None) -> None:
        """
        Método abstracto para movimiento. Debe ser implementado por subclases.
        
        Args:
            maze (List[List[int]]): Laberinto actual.
            pacman_position (tuple[int, int], opcional): Posición de Pac-Man (usado por perseguidores).
            pacman_direction (str, opcional): Dirección de Pac-Man (usado por perseguidores).
        """
        raise NotImplementedError("Subclasses must implement move()")

    def update_vulnerability(self):
        """
        Actualiza el estado de vulnerabilidad del fantasma.
        """
        if self.is_vulnerable:
            self.vulnerable_timer -= 1
            self.frightened_timer -= 1
            if self.vulnerable_timer <= 0:
                self.is_vulnerable = False
                self.vulnerable_timer = 0
                self.frightened_timer = 0

    def interpolate_position(self):
        """
        Interpola la posición flotante hacia la posición entera.
        """
        target_x = float(self.position[0])
        target_y = float(self.position[1])
        
        # Movimiento suave hacia la celda objetivo
        if abs(self.float_pos[0] - target_x) > self.speed:
            if self.float_pos[0] < target_x:
                self.float_pos[0] += self.speed
            else:
                self.float_pos[0] -= self.speed
        else:
            self.float_pos[0] = target_x

        if abs(self.float_pos[1] - target_y) > self.speed:
            if self.float_pos[1] < target_y:
                self.float_pos[1] += self.speed
            else:
                self.float_pos[1] -= self.speed
        else:
            self.float_pos[1] = target_y

    def _get_valid_moves(self, maze: List[List[int]]) -> List[tuple[int, int]]:
        """
        Obtiene los movimientos válidos desde la posición actual, evitando el U-turn.
        """
        current_row, current_col = self.position
        valid_moves = []
        for dr, dc in self.directions:
            new_row, new_col = current_row + dr, current_col + dc
            # Verificar límites
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                # Verificar que sea camino
                if maze[new_row][new_col] == 0:
                    # Evitar girar en U (moverse en la dirección opuesta a la anterior)
                    if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                        valid_moves.append((new_row, new_col))
        return valid_moves

    def _choose_random_move(self, valid_moves: List[tuple[int, int]]) -> Optional[tuple[int, int]]:
        """
        Elige un movimiento aleatorio de la lista de movimientos válidos.
        """
        if valid_moves:
            return random.choice(valid_moves)
        return None

    def _move_towards_target(self, maze: List[List[int]], target: tuple[int, int]) -> Optional[tuple[int, int]]:
        """
        Intenta moverse hacia un objetivo usando distancia de Manhattan.
        """
        current_row, current_col = self.position
        best_move = None
        best_distance = float('inf')

        for dr, dc in self.directions:
            new_row, new_col = current_row + dr, current_col + dc
            if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
                if maze[new_row][new_col] == 0:
                    # Evitar girar en U
                    if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                        dist = abs(new_row - target[0]) + abs(new_col - target[1])
                        if dist < best_distance:
                            best_distance = dist
                            best_move = (new_row, new_col)

        return best_move


class Blinky(Ghost):
    """
    Fantasma rojo. Persigue directamente a Pac-Man.
    """
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "blinky")

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, pacman_direction: Optional[str] = None) -> None:
        self.move_counter += 1
        if self.move_counter < 20:  # Moverse cada 20 frames
            self.interpolate_position()
            self.update_vulnerability()
            return
        self.move_counter = 0

        if not pacman_position:
            # Si no hay posición de PacMan, moverse aleatoriamente
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            if self.is_vulnerable:
                # Si está vulnerable, moverse aleatoriamente
                valid_moves = self._get_valid_moves(maze)
                next_pos = self._choose_random_move(valid_moves)
            else:
                # Si no está vulnerable, perseguir a PacMan
                next_pos = self._move_towards_target(maze, pacman_position)

        if next_pos:
            self.position = list(next_pos)
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
        # Si no hay movimiento posible, mantener la posición actual

        self.interpolate_position()
        self.update_vulnerability()


class Pinky(Ghost):
    """
    Fantasma rosa. Intenta ir a la casilla que está 2 pasos adelante de donde mira Pac-Man.
    """
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "pinky")

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, pacman_direction: Optional[str] = None) -> None:
        self.move_counter += 1
        if self.move_counter < 20:  # Moverse cada 20 frames
            self.interpolate_position()
            self.update_vulnerability()
            return
        self.move_counter = 0

        if not pacman_position or not pacman_direction:
            # Si no hay posición o dirección de PacMan, moverse aleatoriamente
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            if self.is_vulnerable:
                # Si está vulnerable, moverse aleatoriamente
                valid_moves = self._get_valid_moves(maze)
                next_pos = self._choose_random_move(valid_moves)
            else:
                # Calcular objetivo: 2 pasos adelante de PacMan
                target_offset = {"UP": (-2, 0), "DOWN": (2, 0), "LEFT": (0, -2), "RIGHT": (0, 2)}
                offset = target_offset.get(pacman_direction, (0, 0))
                target = (pacman_position[0] + offset[0], pacman_position[1] + offset[1])
                # Asegurarse de que el objetivo esté dentro del laberinto
                rows, cols = len(maze), len(maze[0])
                target = (max(0, min(rows - 1, target[0])), max(0, min(cols - 1, target[1])))

                # Moverse hacia el objetivo calculado
                next_pos = self._move_towards_target(maze, target)

        if next_pos:
            self.position = list(next_pos)
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
        # Si no hay movimiento posible, mantener la posición actual

        self.interpolate_position()
        self.update_vulnerability()


class Inky(Ghost):
    """
    Fantasma cyan. Comportamiento más impredecible.
    Aquí lo simplificamos como un RandomGhost que puede alejarse de PacMan si está cerca.
    """
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "inky")

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, pacman_direction: Optional[str] = None) -> None:
        self.move_counter += 1
        if self.move_counter < 20:  # Moverse cada 20 frames
            self.interpolate_position()
            self.update_vulnerability()
            return
        self.move_counter = 0

        if not pacman_position:
            # Si no hay posición de PacMan, moverse aleatoriamente
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            if self.is_vulnerable:
                # Si está vulnerable, moverse aleatoriamente
                valid_moves = self._get_valid_moves(maze)
                next_pos = self._choose_random_move(valid_moves)
            else:
                # Calcular distancia a PacMan
                dist_to_pacman = math.sqrt((self.position[0] - pacman_position[0])**2 + (self.position[1] - pacman_position[1])**2)
                if dist_to_pacman < 5: # Si está cerca, alejarse
                    # Moverse en dirección opuesta a PacMan
                    dx = self.position[0] - pacman_position[0]
                    dy = self.position[1] - pacman_position[1]
                    # Normalizar el vector de dirección
                    length = max(1, math.sqrt(dx**2 + dy**2))
                    dx /= length
                    dy /= length
                    # Buscar movimientos válidos que se alejen de PacMan
                    current_row, current_col = self.position
                    best_move = None
                    best_dot_product = float('-inf') # El producto punto más negativo indica la dirección opuesta
                    for dr, dc in self.directions:
                        new_row, new_col = current_row + dr, current_col + dc
                        if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]) and maze[new_row][new_col] == 0:
                            # Evitar girar en U
                            if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                                # Producto punto con la dirección opuesta a PacMan
                                dot_product = dr * dx + dc * dy
                                if dot_product > best_dot_product:
                                    best_dot_product = dot_product
                                    best_move = (new_row, new_col)
                    next_pos = best_move
                else: # Si está lejos, moverse aleatoriamente
                    valid_moves = self._get_valid_moves(maze)
                    next_pos = self._choose_random_move(valid_moves)

        if next_pos:
            self.position = list(next_pos)
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
        # Si no hay movimiento posible, mantener la posición actual

        self.interpolate_position()
        self.update_vulnerability()


class Clyde(Ghost):
    """
    Fantasma naranja. Se aleja si está cerca de PacMan, persigue si está lejos.
    """
    def __init__(self, initial_position: tuple[int, int]):
        super().__init__(initial_position, "clyde")

    def move(self, maze: List[List[int]], pacman_position: Optional[tuple[int, int]] = None, pacman_direction: Optional[str] = None) -> None:
        self.move_counter += 1
        if self.move_counter < 20:  # Moverse cada 20 frames
            self.interpolate_position()
            self.update_vulnerability()
            return
        self.move_counter = 0

        if not pacman_position:
            # Si no hay posición de PacMan, moverse aleatoriamente
            valid_moves = self._get_valid_moves(maze)
            next_pos = self._choose_random_move(valid_moves)
        else:
            if self.is_vulnerable:
                # Si está vulnerable, moverse aleatoriamente
                valid_moves = self._get_valid_moves(maze)
                next_pos = self._choose_random_move(valid_moves)
            else:
                # Calcular distancia a PacMan
                dist_to_pacman = math.sqrt((self.position[0] - pacman_position[0])**2 + (self.position[1] - pacman_position[1])**2)
                if dist_to_pacman < 8: # Si está cerca, alejarse
                    # Moverse en dirección opuesta a PacMan
                    dx = self.position[0] - pacman_position[0]
                    dy = self.position[1] - pacman_position[1]
                    # Normalizar el vector de dirección
                    length = max(1, math.sqrt(dx**2 + dy**2))
                    dx /= length
                    dy /= length
                    # Buscar movimientos válidos que se alejen de PacMan
                    current_row, current_col = self.position
                    best_move = None
                    best_dot_product = float('-inf') # El producto punto más negativo indica la dirección opuesta
                    for dr, dc in self.directions:
                        new_row, new_col = current_row + dr, current_col + dc
                        if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]) and maze[new_row][new_col] == 0:
                            # Evitar girar en U
                            if (dr, dc) != (-self.last_direction[0], -self.last_direction[1]):
                                # Producto punto con la dirección opuesta a PacMan
                                dot_product = dr * dx + dc * dy
                                if dot_product > best_dot_product:
                                    best_dot_product = dot_product
                                    best_move = (new_row, new_col)
                    next_pos = best_move
                else: # Si está lejos, perseguir
                    next_pos = self._move_towards_target(maze, pacman_position)

        if next_pos:
            self.position = list(next_pos)
            self.last_direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
        # Si no hay movimiento posible, mantener la posición actual

        self.interpolate_position()
        self.update_vulnerability()

# --- Fin de entities/ghosts.py ---