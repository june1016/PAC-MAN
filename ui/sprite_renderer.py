"""
Módulo para renderizar el mundo del juego usando sprites externos.
Carga y dibuja los sprites desde archivos PNG, manteniendo una estética pixel art.
"""
import pygame
import os
from typing import Dict, Optional

class SpriteRenderer:
    """Gestor de sprites para el juego PACMAN."""

    def __init__(self, assets_dir: str = "assets/images"):
        self.assets_dir = assets_dir
        self.sprites: Dict[str, any] = {}
        
        self.pacman_animation_frame = 0
        self.pacman_animation_counter = 0
        self.pacman_animation_speed = 5
        
        self._load_sprites()

    def _load_sprites(self) -> None:
        """Carga todos los sprites necesarios."""
        print("[RENDERER] Cargando sprites...")
        
        # Cargar animaciones de Pac-Man
        pacman_dirs = ["up", "down", "left", "right"]
        for direction in pacman_dirs:
            self.sprites[f"pacman_{direction}"] = {}
            for i in range(1, 4):
                filepath = os.path.join(self.assets_dir, f"pacman-{direction}", f"{i}.png")
                sprite = self._load_single_sprite(filepath)
                if sprite:
                    self.sprites[f"pacman_{direction}"][i-1] = sprite
                else:
                    self.sprites[f"pacman_{direction}"][i-1] = self._create_fallback_sprite((255, 255, 0))
        
        # Cargar fantasmas
        ghost_names = ["blinky", "pinky", "inky", "clyde", "blue_ghost"]
        ghost_colors = {
            "blinky": (255, 0, 0),
            "pinky": (255, 184, 255),
            "inky": (0, 255, 255),
            "clyde": (255, 184, 82),
            "blue_ghost": (50, 50, 255)
        }
        
        for name in ghost_names:
            filepath = os.path.join(self.assets_dir, "ghosts", f"{name}.png")
            sprite = self._load_single_sprite(filepath)
            self.sprites[name] = sprite if sprite else self._create_fallback_sprite(ghost_colors[name])
        
        # Cargar comida
        food_items = {
            "dot": (255, 255, 255),
            "apple": (255, 0, 0),
            "strawberry": (255, 100, 100)
        }
        
        for name, color in food_items.items():
            filepath = os.path.join(self.assets_dir, "other", f"{name}.png")
            sprite = self._load_single_sprite(filepath)
            
            if sprite:
                self.sprites[name] = sprite
                print(f"[RENDERER] ✓ Sprite {name} cargado: {sprite.get_size()}")
            else:
                size = 8 if name == "dot" else 16
                self.sprites[name] = self._create_fallback_sprite(color, size=size)
                print(f"[RENDERER] ⚠ Usando fallback para {name}")
        
        print(f"[RENDERER] Total sprites: {len(self.sprites)}")

    def _load_single_sprite(self, filepath: str) -> Optional[pygame.Surface]:
        if os.path.exists(filepath):
            try:
                sprite = pygame.image.load(filepath).convert_alpha()
                return sprite
            except pygame.error as e:
                print(f"[RENDERER] ✗ Error cargando {filepath}: {e}")
                return None
        return None

    def _create_fallback_sprite(self, color: tuple, size: int = 16) -> pygame.Surface:
        """Crea un sprite de respaldo (círculo de color sólido)."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
        return surface

    def _get_pacman_sprite(self, direction: str) -> pygame.Surface:
        self.pacman_animation_counter += 1
        if self.pacman_animation_counter >= self.pacman_animation_speed:
            self.pacman_animation_counter = 0
            self.pacman_animation_frame = (self.pacman_animation_frame + 1) % 3
        
        direction_key = direction.lower()
        sprite_dict = self.sprites.get(f"pacman_{direction_key}", {})
        return sprite_dict.get(self.pacman_animation_frame, self._create_fallback_sprite((255, 255, 0)))

    def draw_world(self, screen: pygame.Surface, game_core, cell_size: int = 30) -> None:
        """Dibuja el mundo del juego: laberinto, comida, Pac-Man y fantasmas."""
        if not game_core.maze:
            return
        
        maze_width = len(game_core.maze[0]) * cell_size
        maze_height = len(game_core.maze) * cell_size
        offset_x = (screen.get_width() - maze_width) // 2
        offset_y = (screen.get_height() - maze_height) // 2
        
        self._draw_maze(screen, game_core.maze, offset_x, offset_y, cell_size)
        self._draw_food(screen, game_core.food_positions, offset_x, offset_y, cell_size)
        self._draw_power_pellets(screen, game_core.power_pellet_positions, offset_x, offset_y, cell_size)
        self._draw_pacman(screen, game_core.pacman, offset_x, offset_y, cell_size)
        self._draw_ghosts(screen, game_core.ghosts, offset_x, offset_y, cell_size)

    def _draw_maze(self, screen: pygame.Surface, maze: list, offset_x: int, offset_y: int, cell_size: int) -> None:
        for i, row in enumerate(maze):
            for j, cell in enumerate(row):
                x = offset_x + j * cell_size
                y = offset_y + i * cell_size
                
                if cell == 1:  # WALL
                    pygame.draw.rect(screen, (33, 33, 222), (x, y, cell_size, cell_size))
                    pygame.draw.rect(screen, (66, 66, 255), (x, y, cell_size, cell_size), 1)
                elif cell == 2:  # GHOST_HOUSE
                    pygame.draw.rect(screen, (50, 20, 50), (x, y, cell_size, cell_size))
                elif cell == 3:  # GHOST_DOOR
                    pygame.draw.rect(screen, (255, 100, 255), (x, y, cell_size, cell_size))

    def _draw_food(self, screen: pygame.Surface, food_positions: set, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja la comida normal (dots)."""
        
        # Obtener sprite dot
        dot_sprite = self.sprites.get("dot")
        
        # Si el sprite existe, usarlo
        if dot_sprite and dot_sprite.get_width() > 0:
            # Escalar el sprite a tamaño pequeño
            dot_size = max(4, cell_size // 5)  # Mínimo 4px
            try:
                dot_scaled = pygame.transform.scale(dot_sprite, (dot_size, dot_size))
                
                # Dibujar cada dot usando el sprite
                for row, col in food_positions:
                    x = offset_x + col * cell_size + (cell_size - dot_size) // 2
                    y = offset_y + row * cell_size + (cell_size - dot_size) // 2
                    screen.blit(dot_scaled, (x, y))
            except:
                # Si falla el escalado, usar círculos
                self._draw_food_fallback(screen, food_positions, offset_x, offset_y, cell_size)
        else:
            # Si no hay sprite, usar círculos directos
            self._draw_food_fallback(screen, food_positions, offset_x, offset_y, cell_size)
    
    def _draw_food_fallback(self, screen: pygame.Surface, food_positions: set, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja dots como círculos blancos simples (fallback)."""
        dot_radius = 3
        
        for row, col in food_positions:
            center_x = offset_x + col * cell_size + cell_size // 2
            center_y = offset_y + row * cell_size + cell_size // 2
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), dot_radius)

    def _draw_power_pellets(self, screen: pygame.Surface, pellet_positions: set, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja los power pellets (manzanas)."""
        apple = self.sprites.get("apple")
        
        if apple and apple.get_width() > 0:
            pellet_size = cell_size // 2
            try:
                apple_scaled = pygame.transform.scale(apple, (pellet_size, pellet_size))
                
                for row, col in pellet_positions:
                    x = offset_x + col * cell_size + (cell_size - pellet_size) // 2
                    y = offset_y + row * cell_size + (cell_size - pellet_size) // 2
                    screen.blit(apple_scaled, (x, y))
            except:
                # Fallback: círculos rojos grandes
                for row, col in pellet_positions:
                    center_x = offset_x + col * cell_size + cell_size // 2
                    center_y = offset_y + row * cell_size + cell_size // 2
                    pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), 6)
        else:
            # Fallback: círculos rojos grandes
            for row, col in pellet_positions:
                center_x = offset_x + col * cell_size + cell_size // 2
                center_y = offset_y + row * cell_size + cell_size // 2
                pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), 6)

    def _draw_pacman(self, screen: pygame.Surface, pacman, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja a Pac-Man con animación."""
        pacman_sprite = self._get_pacman_sprite(pacman.direction)
        pacman_scaled = pygame.transform.scale(pacman_sprite, (cell_size, cell_size))
        
        row, col = pacman.position
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size
        screen.blit(pacman_scaled, (x, y))

    def _draw_ghosts(self, screen: pygame.Surface, ghosts: list, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja TODOS los fantasmas (incluso en la casa con semi-transparencia)."""
        for ghost in ghosts:
            # Elegir sprite según estado
            if ghost.is_vulnerable:
                sprite = self.sprites.get("blue_ghost")
            else:
                sprite = self.sprites.get(ghost.ghost_type)
            
            if not sprite:
                continue
            
            ghost_scaled = pygame.transform.scale(sprite, (cell_size, cell_size))
            
            # Si está en casa, aplicar semi-transparencia
            if ghost.in_house:
                ghost_scaled.set_alpha(128)
            else:
                ghost_scaled.set_alpha(255)
            
            row, col = ghost.position
            x = offset_x + col * cell_size
            y = offset_y + row * cell_size
            screen.blit(ghost_scaled, (x, y))