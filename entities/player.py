"""
Módulo que define la entidad controlable por el jugador: Pac-Man.

La clase PacMan gestiona su posición, movimiento restringido al laberinto,
y la interacción con elementos del mundo (como la comida).
"""

from typing import List, Tuple, Set


class PacMan:
    """
    Representa al jugador en el juego PACMAN.
    
    Gestiona la posición, el movimiento validado contra el laberinto,
    y la recolección de comida.
    """

    def __init__(self, initial_position: tuple[int, int], lives: int = 3):
        """
        Inicializa a Pac-Man en una posición dada.
        
        Args:
            initial_position (tuple[int, int]): Posición inicial (fila, columna).
            lives (int): Número inicial de vidas. Por defecto 3.
        """
        self.position = list(initial_position)  # [fila, columna] - mutable
        self.float_pos = [float(self.position[0]), float(self.position[1])]  # [fila, columna] (flotantes)
        self.lives = lives
        self.score = 0
        self.speed = 0.05  # Velocidad de movimiento (ajusta según sea necesario)
        self.direction = "RIGHT"  # Dirección actual ("UP", "DOWN", "LEFT", "RIGHT")
        self.next_direction = None  # Dirección solicitada para el siguiente movimiento

    def move(self, direction: str, maze: List[List[int]], food_positions: Set[tuple[int, int]], power_pellet_positions: Set[tuple[int, int]], sound_manager) -> bool:
        """
        Intenta mover a Pac-Man en la dirección especificada.
        
        El movimiento solo se realiza si la celda destino es transitable (PATH).
        Si hay comida en la nueva posición, se recolecta y se actualiza el puntaje.
        Verifica colisiones antes de actualizar la posición entera.
        
        Args:
            direction (str): Una de 'UP', 'DOWN', 'LEFT', 'RIGHT'.
            maze (List[List[int]]): Laberinto actual (1 = pared, 0 = camino).
            food_positions (Set[tuple[int, int]]): Conjunto de posiciones con comida.
            power_pellet_positions (Set[tuple[int, int]]): Conjunto de posiciones con monedas grandes.
            sound_manager: Gestor de sonido para reproducir efectos.
            
        Returns:
            bool: True si el movimiento fue válido (aunque no se mueva por pared), False si no.
        """
        # Almacenar la dirección solicitada para el siguiente movimiento
        self.next_direction = direction

        # Calcular nueva posición entera según la dirección actual
        new_row, new_col = self.position[0], self.position[1]
        if self.direction == "UP":
            new_row -= 1
        elif self.direction == "DOWN":
            new_row += 1
        elif self.direction == "LEFT":
            new_col -= 1
        elif self.direction == "RIGHT":
            new_col += 1

        # Verificar límites del tablero y colisión con paredes ANTES de actualizar position
        rows, cols = len(maze), len(maze[0])
        if 0 <= new_row < rows and 0 <= new_col < cols and maze[new_row][new_col] == 0:
            # La celda destino es válida, actualizar posición entera
            self.position = [new_row, new_col]
            # Verificar si hay comida en la nueva posición entera
            current_pos = (self.position[0], self.position[1])
            if current_pos in food_positions:
                food_positions.discard(current_pos)
                self.score += 10
                if sound_manager: # Verificar que sound_manager no sea None
                    sound_manager.play_eat_sound()  # Reproducir sonido al comer
            elif current_pos in power_pellet_positions:
                power_pellet_positions.discard(current_pos)
                self.score += 50  # Puntos por moneda grande
                if sound_manager: # Verificar que sound_manager no sea None
                    sound_manager.play_eat_sound()  # Reproducir sonido al comer
            return True
        else:
            # La celda destino está bloqueada o fuera de límites
            # Intentar moverse en la dirección solicitada (next_direction) si es diferente
            if self.next_direction != self.direction:
                new_row, new_col = self.position[0], self.position[1]
                if self.next_direction == "UP":
                    new_row -= 1
                elif self.next_direction == "DOWN":
                    new_row += 1
                elif self.next_direction == "LEFT":
                    new_col -= 1
                elif self.next_direction == "RIGHT":
                    new_col += 1

                # Verificar límites del tablero y colisión con paredes para la dirección solicitada
                if 0 <= new_row < rows and 0 <= new_col < cols and maze[new_row][new_col] == 0:
                    # La celda destino para la dirección solicitada es válida
                    self.direction = self.next_direction
                    self.position = [new_row, new_col]
                    # Verificar si hay comida en la nueva posición entera
                    current_pos = (self.position[0], self.position[1])
                    if current_pos in food_positions:
                        food_positions.discard(current_pos)
                        self.score += 10
                        if sound_manager: # Verificar que sound_manager no sea None
                            sound_manager.play_eat_sound()  # Reproducir sonido al comer
                    elif current_pos in power_pellet_positions:
                        power_pellet_positions.discard(current_pos)
                        self.score += 50  # Puntos por moneda grande
                        if sound_manager: # Verificar que sound_manager no sea None
                            sound_manager.play_eat_sound()  # Reproducir sonido al comer
                    return True
            # Si ninguna dirección es válida, no se mueve
            return False


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

    def lose_life(self) -> bool:
        """
        Reduce en uno la cantidad de vidas.
        
        Returns:
            bool: True si aún le quedan vidas, False si se quedó sin vidas.
        """
        self.lives -= 1
        return self.lives > 0

    def reset_position(self, new_position: tuple[int, int]) -> None:
        """
        Restablece la posición de Pac-Man (usado tras perder una vida).
        
        Args:
            new_position (tuple[int, int]): Nueva posición de inicio.
        """
        self.position = list(new_position)
        self.float_pos = [float(self.position[0]), float(self.position[1])]
        self.direction = "RIGHT" # Reiniciar dirección al spawn
        self.next_direction = None