"""
Módulo central del juego: gestiona el bucle principal, estados, colisiones,
transición de niveles y coordinación entre entidades.
"""

import random
from typing import List, Set, Tuple
# Importamos las constantes del nuevo mapa desde world.board
from world.board import BoardGenerator, DEFAULT_ROWS, DEFAULT_COLS, PATH, PACMAN_SPAWN, GHOST_SPAWN, POWER_PELLET_POSITIONS
from entities.player import PacMan
# Importamos las clases específicas de fantasmas
from entities.ghosts import Blinky, Pinky, Inky, Clyde


class GameState:
    """Enumeración de estados del juego."""
    MENU = "MENU"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"
    PAUSED = "PAUSED"


class GameCore:
    """
    Núcleo del juego PACMAN.
    
    Coordina generación de niveles, movimiento de entidades, colisiones,
    puntaje, vidas y transición entre estados.
    """

    def __init__(self, sound_manager): # Recibir sound_manager como parámetro
        self.game_state = GameState.MENU
        self.level = 1
        self.base_fps = 60  # FPS base en nivel 1
        self.board_gen = BoardGenerator(DEFAULT_ROWS, DEFAULT_COLS) # Usar BoardGenerator
        self.maze: List[List[int]] = []
        self.food_positions: Set[tuple[int, int]] = set()
        # Usamos las posiciones fijas de POWER_PELLET_POSITIONS para las monedas grandes
        self.power_pellet_positions: Set[tuple[int, int]] = set(POWER_PELLET_POSITIONS)
        self.pacman: PacMan = None
        self.ghosts: List = []
        self.walkable_positions: List[tuple[int, int]] = []
        # Usamos las posiciones fijas de GHOST_SPAWN para la casa de fantasmas
        self.ghost_house = GHOST_SPAWN
        self.sound_manager = sound_manager # Almacenar sound_manager
        self.power_pellet_active = False # Indica si una moneda grande está activa
        self.power_pellet_timer = 0 # Contador para el tiempo que dura la moneda grande

    def start_new_game(self) -> None:
        """Inicia un nuevo juego desde el nivel 1."""
        self.level = 1
        self.game_state = GameState.PLAYING
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        self._setup_level()

    def _setup_level(self) -> None:
        """Configura el nivel actual: laberinto, comida, entidades."""
        # Generar laberinto (ahora fijo)
        self.maze = self.board_gen.generate_maze()
        self.walkable_positions = self.board_gen.get_walkable_positions(self.maze)

        print(f"Labyrinth generated: {len(self.maze)}x{len(self.maze[0]) if self.maze else 0}")
        print(f"Food positions: {len(self.food_positions)}")

        # Determinar cantidad de comida (70% de celdas transitables, excluyendo spawns y power pellets)
        exclude_positions = set([PACMAN_SPAWN] + GHOST_SPAWN + list(self.power_pellet_positions))
        num_food = max(10, int(len(self.walkable_positions) * 0.7))

        # Posición de Pac-Man (fija)
        self.pacman = PacMan(PACMAN_SPAWN, lives=3)

        # Crear fantasmas específicos en posiciones fijas
        self.ghosts = []
        ghost_spawn_points = GHOST_SPAWN[:]
        # Asumimos que GHOST_SPAWN tiene al menos 4 posiciones
        if len(ghost_spawn_points) >= 4:
            self.ghosts.append(Blinky(ghost_spawn_points[0]))
            self.ghosts.append(Pinky(ghost_spawn_points[1]))
            self.ghosts.append(Inky(ghost_spawn_points[2]))
            self.ghosts.append(Clyde(ghost_spawn_points[3]))

        # Colocar comida (excluyendo spawns y power pellets)
        self.food_positions = self.board_gen.place_food(
            self.walkable_positions, num_food, exclude_positions=exclude_positions
        )

        # Las monedas grandes ya están definidas en self.power_pellet_positions


    def handle_input(self, direction: str) -> None:
        """
        Procesa la entrada del jugador (teclado).
        
        Args:
            direction (str): 'UP', 'DOWN', 'LEFT', 'RIGHT'.
        """
        if self.game_state == GameState.PLAYING:
            # Pasar self.sound_manager al método move de PacMan
            # La dirección se almacena en PacMan pero el movimiento real se hace en update()
            # Aquí solo almacenamos la dirección solicitada
            self.pacman.next_direction = direction
        elif self.game_state == GameState.PAUSED:
            if direction == "PAUSE":
                self.game_state = GameState.PLAYING

    def update(self) -> None:
        """
        Actualiza la lógica del juego: movimiento de fantasmas, colisiones, progreso.
        """
        if self.game_state != GameState.PLAYING:
            return

        # Actualizar estado de moneda grande
        if self.power_pellet_active:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer <= 0:
                self.power_pellet_active = False
                # Desactivar vulnerabilidad de fantasmas
                for ghost in self.ghosts:
                    ghost.is_vulnerable = False
                    ghost.vulnerable_timer = 0
                    ghost.frightened_timer = 0 # Reiniciar timer de miedo

        # Interpolar posiciones para suavidad
        self.pacman.interpolate_position()
        for ghost in self.ghosts:
            ghost.interpolate_position()

        # Mover PacMan
        # Usamos la dirección almacenada (next_direction) si es válida, o la actual
        # El método move ahora maneja la lógica de cambio de dirección
        # Pasamos la dirección actual como argumento para que el movimiento se realice
        current_dir_map = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        current_dir = current_dir_map.get(self.pacman.direction, (0, 0))
        new_row = self.pacman.position[0] + current_dir[0]
        new_col = self.pacman.position[1] + current_dir[1]

        rows, cols = len(self.maze), len(self.maze[0])
        if 0 <= new_row < rows and 0 <= new_col < cols and self.maze[new_row][new_col] == 0:
            # La celda actual está libre, intentar moverse
            self.pacman.move(self.pacman.direction, self.maze, self.food_positions, self.power_pellet_positions, self.sound_manager)
        else:
            # La celda actual está bloqueada, intentar con la dirección solicitada
            next_dir_map = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
            next_dir = next_dir_map.get(self.pacman.next_direction, (0, 0))
            new_row_next = self.pacman.position[0] + next_dir[0]
            new_col_next = self.pacman.position[1] + next_dir[1]
            if 0 <= new_row_next < rows and 0 <= new_col_next < cols and self.maze[new_row_next][new_col_next] == 0:
                # La celda para la dirección solicitada está libre, cambiar dirección y mover
                self.pacman.direction = self.pacman.next_direction
                self.pacman.move(self.pacman.direction, self.maze, self.food_positions, self.power_pellet_positions, self.sound_manager)
            # Si no, PacMan no se mueve pero mantiene su dirección actual

        # Mover fantasmas (ahora pasamos la posición y dirección de PacMan)
        for ghost in self.ghosts:
            ghost.move(self.maze, tuple(self.pacman.position), self.pacman.direction)

        # Verificar colisión con fantasmas
        for ghost in self.ghosts:
            if self.pacman.position == ghost.position:
                if ghost.is_vulnerable:
                    # Comer fantasma
                    ghost.is_vulnerable = False
                    ghost.vulnerable_timer = 0
                    ghost.frightened_timer = 0
                    # Reiniciar posición del fantasma (a la casa)
                    spawn_candidates = self.ghost_house
                    if spawn_candidates:
                        new_pos = random.choice(spawn_candidates)
                        ghost.position = list(new_pos)
                        ghost.float_pos = [float(ghost.position[0]), float(ghost.position[1])]
                        ghost.last_direction = (0, 0) # Reiniciar dirección al spawn
                    self.pacman.score += 200 # Puntos por comer fantasma (actualizar score de pacman)
                    if self.sound_manager:
                        self.sound_manager.play_eat_sound() # Sonido al comer fantasma
                else:
                    if self.pacman.lose_life():
                        # Reiniciar posición, mantener comida restante
                        spawn_candidates = [
                            pos for pos in self.walkable_positions
                            if 3 <= pos[0] <= DEFAULT_ROWS - 4 and 3 <= pos[1] <= DEFAULT_COLS - 4
                        ]
                        if spawn_candidates:
                            new_pos = random.choice(spawn_candidates)
                            self.pacman.reset_position(new_pos)
                    else:
                        self.game_state = GameState.GAME_OVER
                    break

        # Verificar si se completó el nivel (toda la comida recolectada)
        if not self.food_positions and not self.power_pellet_positions:
            self.level += 1
            self._setup_level()

    def get_fps(self) -> int:
        """
        Devuelve los FPS actuales, ajustados por nivel (dificultad).
        
        Returns:
            int: FPS (mínimo 60, máximo 120).
        """
        return min(120, self.base_fps + (self.level - 1) * 10)

    def get_progress_percentage(self) -> float:
        """
        Calcula el porcentaje de comida recolectada en el nivel actual.
        
        Returns:
            float: Porcentaje de avance (0.0 a 100.0).
        """
        total_food_initial = len(self.food_positions) + len(self.power_pellet_positions) + (self.pacman.score // 10)
        if total_food_initial == 0:
            return 100.0
        collected = self.pacman.score // 10
        return (collected / total_food_initial) * 100

    def is_game_over(self) -> bool:
        return self.game_state == GameState.GAME_OVER

    def is_playing(self) -> bool:
        return self.game_state == GameState.PLAYING

    def is_paused(self) -> bool:
        return self.game_state == GameState.PAUSED