"""
Módulo central del juego: gestiona el bucle principal, estados, colisiones,
transición de niveles y coordinación entre entidades.
"""

import random
from typing import List, Set, Tuple, Optional
from world.board import (
    BoardGenerator, 
    DEFAULT_ROWS, 
    DEFAULT_COLS, 
    TILE_SIZE,
    PACMAN_SPAWN, 
    GHOST_SPAWN, 
    GHOST_HOUSE_EXIT,
    POWER_PELLET_POSITIONS
)
from entities.player import PacMan
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

    def __init__(self, sound_manager):
        """Inicializa el núcleo del juego con gestor de sonido."""
        self.game_state = GameState.MENU
        self.level = 1
        self.base_fps = 60
        
        # Sistema de tablero
        self.board_gen = BoardGenerator(DEFAULT_ROWS, DEFAULT_COLS)
        self.maze: List[List[int]] = []
        
        # Sistema de comida
        self.food_positions: Set[Tuple[int, int]] = set()
        self.power_pellet_positions: Set[Tuple[int, int]] = set()
        self.initial_food_count = 0
        
        # Entidades
        self.pacman: Optional[PacMan] = None
        self.ghosts: List = []
        
        # Sistema de power pellets
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        self.power_pellet_duration = 540
        
        # Audio
        self.sound_manager = sound_manager
        
        # Sistema de release de fantasmas
        self.ghost_release_timer = 0
        self.ghosts_released = 0

    def start_new_game(self) -> None:
        """Inicia un nuevo juego desde el nivel 1."""
        self.level = 1
        self.game_state = GameState.PLAYING
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        self.ghosts_released = 0
        self._setup_level()

    def _setup_level(self) -> None:
        """Configura el nivel actual: laberinto, comida, entidades."""
        # Generar laberinto fijo
        self.maze = self.board_gen.generate_maze()
        
        # Configurar exclusiones para comida
        exclude_positions = {PACMAN_SPAWN}
        exclude_positions.update(GHOST_SPAWN)
        
        # Colocar comida en TODAS las celdas transitables
        self.food_positions = self.board_gen.place_all_food(exclude_positions)
        
        # Remover posiciones de power pellets de food_positions
        for pellet_pos in POWER_PELLET_POSITIONS:
            self.food_positions.discard(pellet_pos)
        
        # Configurar power pellets
        self.power_pellet_positions = self.board_gen.get_power_pellets()
        
        # Guardar cantidad inicial
        self.initial_food_count = len(self.food_positions) + len(self.power_pellet_positions)
        
        # Crear Pac-Man
        self.pacman = PacMan(PACMAN_SPAWN, lives=3)
        
        # Crear fantasmas
        self.ghosts = []
        if len(GHOST_SPAWN) >= 4:
            self.ghosts.append(Blinky(GHOST_SPAWN[0]))
            self.ghosts.append(Pinky(GHOST_SPAWN[1]))
            self.ghosts.append(Inky(GHOST_SPAWN[2]))
            self.ghosts.append(Clyde(GHOST_SPAWN[3]))
        
        # Sistema de release
        self.ghost_release_timer = 0
        self.ghosts_released = 1
        if self.ghosts:
            self.ghosts[0].in_house = False
        
        # ==================== AJUSTAR INTENSIDAD DE MÚSICA ====================
        if self.sound_manager:
            self.sound_manager.set_level_intensity(self.level)
            intensity_msg = self.sound_manager.get_intensity_message(self.level)
            print(f"[AUDIO] {intensity_msg}")
        
        print(f"[LEVEL {self.level}] Laberinto: {len(self.maze)}x{len(self.maze[0])}")
        print(f"[LEVEL {self.level}] Comida (dots): {len(self.food_positions)}")
        print(f"[LEVEL {self.level}] Power Pellets: {len(self.power_pellet_positions)}")
        print(f"[LEVEL {self.level}] Total comida: {self.initial_food_count}")

    def handle_input(self, direction: str) -> None:
        """Procesa la entrada del jugador (teclado)."""
        if self.game_state == GameState.PLAYING:
            if direction == "PAUSE":
                self.game_state = GameState.PAUSED
                if self.sound_manager:
                    self.sound_manager.pause_music()
            else:
                self.pacman.next_direction = direction
        
        elif self.game_state == GameState.PAUSED:
            if direction == "PAUSE":
                self.game_state = GameState.PLAYING
                if self.sound_manager:
                    self.sound_manager.resume_music()

    def update(self) -> None:
        """Actualiza la lógica del juego."""
        if self.game_state != GameState.PLAYING:
            return

        # Sistema de power pellets
        if self.power_pellet_active:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer <= 0:
                self._deactivate_power_pellet()

        # Movimiento de Pac-Man
        self._update_pacman_movement()

        # Sistema de release de fantasmas
        self._update_ghost_release()

        # Movimiento de fantasmas
        for ghost in self.ghosts:
            if not ghost.in_house:
                target_pos = self._get_ghost_target(ghost)
                ghost.move(self.maze, target_pos, self.board_gen)
            else:
                if hasattr(ghost, 'respawn_timer') and ghost.respawn_timer > 0:
                    ghost.respawn_timer -= 1
                    
                    if ghost.respawn_timer % 60 == 0:
                        print(f"[RESPAWN] {ghost.ghost_type} sale en {ghost.respawn_timer // 60}seg")
                    
                    if ghost.respawn_timer == 0:
                        ghost.in_house = False
                        ghost.position = list(GHOST_HOUSE_EXIT)
                        print(f"[RESPAWN] ¡{ghost.ghost_type} LIBERADO!")
                else:
                    self._ghost_house_behavior(ghost)

        # Colisiones con fantasmas
        self._check_ghost_collisions()

        # Verificar nivel completo
        if not self.food_positions and not self.power_pellet_positions:
            self._advance_level()

    def _update_pacman_movement(self) -> None:
        """Maneja el movimiento de Pac-Man."""
        self.pacman.move_delay += 1
        if self.pacman.move_delay < self.pacman.move_frequency:
            return
        
        self.pacman.move_delay = 0
        
        direction_map = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }
        
        if self.pacman.next_direction:
            dr, dc = direction_map.get(self.pacman.next_direction, (0, 0))
            new_row = self.pacman.position[0] + dr
            new_col = self.pacman.position[1] + dc
            
            if self.board_gen.can_pacman_move_to(new_row, new_col):
                self.pacman.direction = self.pacman.next_direction
                self.pacman.position = [new_row, new_col]
                self._check_food_collision()
                return
        
        dr, dc = direction_map.get(self.pacman.direction, (0, 0))
        new_row = self.pacman.position[0] + dr
        new_col = self.pacman.position[1] + dc
        
        new_row, new_col = self.board_gen.handle_tunnel_teleport(new_row, new_col)
        
        if self.board_gen.can_pacman_move_to(new_row, new_col):
            self.pacman.position = [new_row, new_col]
            self._check_food_collision()

    def _check_food_collision(self) -> None:
        """Verifica si Pac-Man comió comida."""
        pos_tuple = tuple(self.pacman.position)
        
        if pos_tuple in self.food_positions:
            self.food_positions.remove(pos_tuple)
            self.pacman.score += 10
            if self.sound_manager:
                self.sound_manager.play_eat_sound()
        
        elif pos_tuple in self.power_pellet_positions:
            self.power_pellet_positions.remove(pos_tuple)
            self.pacman.score += 50
            self._activate_power_pellet()
            if self.sound_manager:
                self.sound_manager.play_eat_sound()

    def _activate_power_pellet(self) -> None:
        """Activa el modo de vulnerabilidad de fantasmas."""
        self.power_pellet_active = True
        self.power_pellet_timer = self.power_pellet_duration
        
        for ghost in self.ghosts:
            if not ghost.in_house:
                ghost.is_vulnerable = True
                ghost.vulnerable_timer = self.power_pellet_duration

    def _deactivate_power_pellet(self) -> None:
        """Desactiva el modo de vulnerabilidad."""
        self.power_pellet_active = False
        for ghost in self.ghosts:
            ghost.is_vulnerable = False
            ghost.vulnerable_timer = 0

    def _update_ghost_release(self) -> None:
        """Sistema de release secuencial de fantasmas."""
        if self.ghosts_released >= len(self.ghosts):
            return
        
        self.ghost_release_timer += 1
        
        release_times = [0, 120, 240, 360]
        
        for i, release_time in enumerate(release_times):
            if i < self.ghosts_released:
                continue
            
            if self.ghost_release_timer >= release_time:
                if i < len(self.ghosts):
                    self.ghosts[i].in_house = False
                    self.ghosts[i].position = list(GHOST_HOUSE_EXIT)
                    self.ghosts_released += 1
                    print(f"[RELEASE] Fantasma {i} liberado")

    def _ghost_house_behavior(self, ghost) -> None:
        """Movimiento de fantasma dentro de la casa."""
        if not hasattr(ghost, 'house_direction'):
            ghost.house_direction = 1
            ghost.house_delay = 0
        
        ghost.house_delay += 1
        if ghost.house_delay < 15:
            return
        
        ghost.house_delay = 0
        
        new_row = ghost.position[0] + ghost.house_direction
        
        if new_row < GHOST_SPAWN[0][0] - 1 or new_row > GHOST_SPAWN[0][0] + 1:
            ghost.house_direction *= -1
        else:
            ghost.position[0] = new_row

    def _get_ghost_target(self, ghost) -> Tuple[int, int]:
        """Determina el objetivo del fantasma."""
        if ghost.is_vulnerable:
            return self._get_scatter_target(ghost, flee=True)
        
        if isinstance(ghost, Blinky):
            return tuple(self.pacman.position)
        
        elif isinstance(ghost, Pinky):
            direction_map = {
                "UP": (-4, 0),
                "DOWN": (4, 0),
                "LEFT": (0, -4),
                "RIGHT": (0, 4)
            }
            dr, dc = direction_map.get(self.pacman.direction, (0, 0))
            target_row = self.pacman.position[0] + dr
            target_col = self.pacman.position[1] + dc
            return (target_row, target_col)
        
        elif isinstance(ghost, Inky):
            distance = abs(ghost.position[0] - self.pacman.position[0]) + \
                      abs(ghost.position[1] - self.pacman.position[1])
            if distance < 8:
                return tuple(self.pacman.position)
            else:
                return self._get_scatter_target(ghost)
        
        elif isinstance(ghost, Clyde):
            distance = abs(ghost.position[0] - self.pacman.position[0]) + \
                      abs(ghost.position[1] - self.pacman.position[1])
            if distance > 8:
                return tuple(self.pacman.position)
            else:
                return self._get_scatter_target(ghost)
        
        return tuple(self.pacman.position)

    def _get_scatter_target(self, ghost, flee: bool = False) -> Tuple[int, int]:
        """Devuelve posición de esquina para modo scatter."""
        corners = [
            (1, 1),
            (1, DEFAULT_COLS - 2),
            (DEFAULT_ROWS - 2, 1),
            (DEFAULT_ROWS - 2, DEFAULT_COLS - 2)
        ]
        
        if flee:
            distances = [
                abs(corner[0] - self.pacman.position[0]) + 
                abs(corner[1] - self.pacman.position[1])
                for corner in corners
            ]
            return corners[distances.index(max(distances))]
        else:
            ghost_corners = {
                Blinky: corners[1],
                Pinky: corners[0],
                Inky: corners[3],
                Clyde: corners[2]
            }
            return ghost_corners.get(type(ghost), corners[0])

    def _check_ghost_collisions(self) -> None:
        """Verifica colisiones entre Pac-Man y fantasmas."""
        for ghost in self.ghosts:
            if ghost.in_house:
                continue
            
            if self.pacman.position == ghost.position:
                if ghost.is_vulnerable:
                    self._eat_ghost(ghost)
                else:
                    self._pacman_dies()
                break

    def _eat_ghost(self, ghost) -> None:
        """Pac-Man come un fantasma vulnerable."""
        ghost.is_vulnerable = False
        ghost.vulnerable_timer = 0
        
        ghost_index = self.ghosts.index(ghost)
        ghost.position = list(GHOST_SPAWN[ghost_index])
        
        ghost.respawn_timer = 180
        ghost.in_house = True
        ghost.just_teleported = True  # Para renderizado suave
        
        self.pacman.score += 200
        if self.sound_manager:
            self.sound_manager.play_eat_sound()
        
        print(f"[GHOST EATEN] {ghost.ghost_type} vuelve en 3seg | +200pts | Score: {self.pacman.score}")

    def _pacman_dies(self) -> None:
        """Pac-Man pierde una vida."""
        if self.sound_manager:
            self.sound_manager.play_death_sound()
        
        if self.pacman.lose_life():
            self.pacman.reset_position(PACMAN_SPAWN)
            
            for i, ghost in enumerate(self.ghosts):
                ghost.position = list(GHOST_SPAWN[i])
                ghost.in_house = True
                ghost.is_vulnerable = False
            
            self.ghosts_released = 1
            if self.ghosts:
                self.ghosts[0].in_house = False
            
            print(f"[DEATH] Vidas restantes: {self.pacman.lives}")
        else:
            self.game_state = GameState.GAME_OVER
            print(f"[GAME OVER] Score final: {self.pacman.score}")

    def _advance_level(self) -> None:
        """Avanza al siguiente nivel."""
        self.level += 1
        print(f"[LEVEL UP] ¡Nivel {self.level} alcanzado!")
        
        # ==================== AJUSTAR INTENSIDAD DE MÚSICA ====================
        if self.sound_manager:
            self.sound_manager.set_level_intensity(self.level)
            intensity_msg = self.sound_manager.get_intensity_message(self.level)
            print(f"[AUDIO] {intensity_msg}")
        
        self._setup_level()

    # Getters
    def get_fps(self) -> int:
        return min(120, self.base_fps + (self.level - 1) * 10)

    def get_progress_percentage(self) -> float:
        if self.initial_food_count == 0:
            return 100.0
        
        remaining = len(self.food_positions) + len(self.power_pellet_positions)
        collected = self.initial_food_count - remaining
        return (collected / self.initial_food_count) * 100

    def is_game_over(self) -> bool:
        return self.game_state == GameState.GAME_OVER

    def is_playing(self) -> bool:
        return self.game_state == GameState.PLAYING

    def is_paused(self) -> bool:
        return self.game_state == GameState.PAUSED