"""
Módulo para renderizar el mundo del juego usando sprites externos.

Carga y dibuja los sprites desde archivos PNG, manteniendo una estética pixel art 16x16.
"""

import pygame
import os


class SpriteRenderer:
    """
    Gestor de sprites para el juego PACMAN.
    
    Carga y dibuja los sprites desde archivos PNG.
    """

    def __init__(self, assets_dir: str = "assets/images"):
        self.assets_dir = assets_dir
        self.sprites = {}
        self.frame_counter = 0
        self.pacman_animation_frame = 1 # Frame actual de la animación de PacMan (1, 2 o 3)
        self.pacman_animation_counter = 0 # Contador para la animación de PacMan
        self._load_sprites()

    def _load_sprites(self) -> None:
        """Carga todos los sprites necesarios."""
        # Cargar PacMan (por dirección)
        pacman_dirs = ["up", "down", "left", "right"]
        for direction in pacman_dirs:
            self.sprites[f"pacman_{direction}"] = {}
            for i in range(1, 4): # Frames 1, 2, 3
                filepath = os.path.join(self.assets_dir, f"pacman-{direction}", f"{i}.png")
                if os.path.exists(filepath):
                    try:
                        sprite = pygame.image.load(filepath).convert_alpha()
                        self.sprites[f"pacman_{direction}"][i] = sprite
                        print(f"Cargado sprite: {filepath}")
                    except pygame.error as e:
                        print(f"Error al cargar {filepath}: {e}")
                        self.sprites[f"pacman_{direction}"][i] = None
                else:
                    print(f"No encontrado: {filepath}")
                    self.sprites[f"pacman_{direction}"][i] = None

        # Cargar Fantasmas
        ghost_names = ["blinky", "pinky", "inky", "clyde", "blue_ghost"]
        for name in ghost_names:
            filepath = os.path.join(self.assets_dir, "ghosts", f"{name}.png")
            if os.path.exists(filepath):
                try:
                    sprite = pygame.image.load(filepath).convert_alpha()
                    self.sprites[name] = sprite
                    print(f"Cargado sprite: {filepath}")
                except pygame.error as e:
                    print(f"Error al cargar {filepath}: {e}")
                    self.sprites[name] = None
            else:
                print(f"No encontrado: {filepath}")
                self.sprites[name] = None

        # Cargar Comida
        food_names = ["dot", "apple", "strawberry"]
        for name in food_names:
            filepath = os.path.join(self.assets_dir, "other", f"{name}.png")
            if os.path.exists(filepath):
                try:
                    sprite = pygame.image.load(filepath).convert_alpha()
                    self.sprites[name] = sprite
                    print(f"Cargado sprite: {filepath}")
                except pygame.error as e:
                    print(f"Error al cargar {filepath}: {e}")
                    self.sprites[name] = None
            else:
                print(f"No encontrado: {filepath}")
                self.sprites[name] = None

    def _get_pacman_sprite(self, direction: str) -> pygame.Surface:
        """
        Obtiene el sprite actual de PacMan según la dirección y la animación.
        """
        # Actualizar animación de PacMan
        self.pacman_animation_counter += 1
        if self.pacman_animation_counter >= 10: # Cambiar frame cada 10 ticks (ajusta según sea necesario)
            self.pacman_animation_counter = 0
            # Alternar entre frames 1 y 2, manteniendo 3 (boca cerrada) por un momento
            # Ej: 1, 2, 1, 2, 3, 3, 3, 3, 1, 2, ...
            # Usamos un contador interno para el frame
            if self.pacman_animation_frame == 1:
                self.pacman_animation_frame = 2
            elif self.pacman_animation_frame == 2:
                self.pacman_animation_frame = 1
            # Si está en 3, lo dejamos un rato (ajusta el contador arriba)
            # o se puede usar un ciclo más complejo si se quiere que 3 aparezca menos frecuente

        # Devolver el sprite correspondiente a la dirección y frame actual
        return self.sprites.get(f"pacman_{direction}", {}).get(self.pacman_animation_frame, None)

    def draw_world(self, screen: pygame.Surface, game_core, cell_size: int = 32) -> None:
        """
        Dibuja el mundo del juego: laberinto, comida, Pac-Man y fantasmas.
        
        Args:
            screen (pygame.Surface): Superficie de Pygame para dibujar.
            game_core (GameCore): Datos del juego en curso.
            cell_size (int): Tamaño en píxeles de cada celda.
        """
        if not game_core.maze or not game_core.walkable_positions:
            return

        # Calcular offset para centrar el laberinto
        maze_width = len(game_core.maze[0]) * cell_size
        maze_height = len(game_core.maze) * cell_size
        offset_x = (screen.get_width() - maze_width) // 2
        offset_y = (screen.get_height() - maze_height) // 2

        # Dibujar laberinto con colores sólidos (paredes azules, fondo negro)
        for i, row in enumerate(game_core.maze):
            for j, cell in enumerate(row):
                x = offset_x + j * cell_size
                y = offset_y + i * cell_size
                if cell == 1:  # Pared
                    pygame.draw.rect(screen, (50, 50, 255), (x, y, cell_size, cell_size))

        # Dibujar comida (dot)
        dot = self.sprites.get("dot")
        if dot:
            dot_scaled = pygame.transform.scale(dot, (cell_size // 2, cell_size // 2))
            for food_y, food_x in game_core.food_positions:
                x = offset_x + food_x * cell_size + cell_size // 4
                y = offset_y + food_y * cell_size + cell_size // 4
                screen.blit(dot_scaled, (x, y))

        # Dibujar power-ups (apple)
        apple = self.sprites.get("apple")
        if apple:
            apple_scaled = pygame.transform.scale(apple, (cell_size // 2, cell_size // 2))
            for food_y, food_x in game_core.power_pellet_positions:
                x = offset_x + food_x * cell_size + cell_size // 4
                y = offset_y + food_y * cell_size + cell_size // 4
                screen.blit(apple_scaled, (x, y))

        # Dibujar Pac-Man
        pacman_direction_map = {
            "UP": "up",
            "DOWN": "down",
            "LEFT": "left",
            "RIGHT": "right"
        }
        pacman_direction = pacman_direction_map.get(game_core.pacman.direction, "right")
        pacman_sprite = self._get_pacman_sprite(pacman_direction)
        if pacman_sprite:
            pacman_scaled = pygame.transform.scale(pacman_sprite, (cell_size, cell_size))
            px, py = game_core.pacman.float_pos
            x = offset_x + py * cell_size
            y = offset_y + px * cell_size
            screen.blit(pacman_scaled, (x, y))

        # Dibujar fantasmas
        for ghost in game_core.ghosts:
            ghost_sprite_name = "blue_ghost" if getattr(ghost, "is_vulnerable", False) else getattr(ghost, "ghost_type", "blinky")
            ghost_sprite = self.sprites.get(ghost_sprite_name)
            if ghost_sprite:
                ghost_scaled = pygame.transform.scale(ghost_sprite, (cell_size, cell_size))
                gx, gy = ghost.float_pos
                x = offset_x + gy * cell_size
                y = offset_y + gx * cell_size
                screen.blit(ghost_scaled, (x, y))

        # Incrementar frame_counter global
        self.frame_counter += 1
        if self.frame_counter >= 10:
            self.frame_counter = 0