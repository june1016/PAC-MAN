"""
Módulo para renderizar el mundo del juego usando sprites externos.
Con interpolación suave para movimiento fluido y manejo de teletransportes.
"""
import pygame
import os
from typing import Dict, Optional, Tuple


class SpriteRenderer:
    """Gestor de sprites para el juego PACMAN."""

    def __init__(self, assets_dir: str = "assets/images"):
        self.assets_dir = assets_dir
        self.sprites: Dict[str, any] = {}
        
        self.pacman_animation_frame = 0
        self.pacman_animation_counter = 0
        self.pacman_animation_speed = 5
        
        # Posiciones interpoladas para movimiento suave
        self.pacman_smooth_pos = [0.0, 0.0]
        self.ghost_smooth_pos = {}  # {ghost_id: [row, col]}
        self.interpolation_speed = 0.35  # Velocidad de interpolación (0.0-1.0)
        
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
            else:
                size = 8 if name == "dot" else 16
                self.sprites[name] = self._create_fallback_sprite(color, size=size)
        
        print(f"[RENDERER] Total sprites: {len(self.sprites)}")

    def _load_single_sprite(self, filepath: str) -> Optional[pygame.Surface]:
        if os.path.exists(filepath):
            try:
                sprite = pygame.image.load(filepath).convert_alpha()
                return sprite
            except pygame.error:
                return None
        return None

    def _create_fallback_sprite(self, color: tuple, size: int = 16) -> pygame.Surface:
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

    def _interpolate_position(
        self, 
        current_smooth: list, 
        target: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Interpola suavemente entre posición actual y objetivo.
        Detecta teletransportes (túneles, respawns) y los maneja instantáneamente.
        
        Args:
            current_smooth: Posición suavizada actual [row, col]
            target: Posición objetivo del grid (row, col)
            
        Returns:
            (row_smooth, col_smooth) interpolado
        """
        target_row = float(target[0])
        target_col = float(target[1])
        
        # Detectar teletransporte (salto grande > 5 celdas en cualquier dirección)
        distance_row = abs(current_smooth[0] - target_row)
        distance_col = abs(current_smooth[1] - target_col)
        
        if distance_row > 5 or distance_col > 5:
            # Teletransporte detectado (túnel lateral o respawn de fantasma)
            # Snap inmediatamente sin interpolación
            current_smooth[0] = target_row
            current_smooth[1] = target_col
            return (current_smooth[0], current_smooth[1])
        
        # Interpolación lineal normal (lerp)
        current_smooth[0] += (target_row - current_smooth[0]) * self.interpolation_speed
        current_smooth[1] += (target_col - current_smooth[1]) * self.interpolation_speed
        
        # Snap al objetivo cuando está muy cerca (evita oscilaciones)
        if abs(current_smooth[0] - target_row) < 0.01:
            current_smooth[0] = target_row
        if abs(current_smooth[1] - target_col) < 0.01:
            current_smooth[1] = target_col
        
        return (current_smooth[0], current_smooth[1])

    def draw_world(self, screen: pygame.Surface, game_core, cell_size: int = 30) -> None:
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
                
                if cell == 1:
                    pygame.draw.rect(screen, (33, 33, 222), (x, y, cell_size, cell_size))
                    pygame.draw.rect(screen, (66, 66, 255), (x, y, cell_size, cell_size), 1)
                elif cell == 2:
                    pygame.draw.rect(screen, (50, 20, 50), (x, y, cell_size, cell_size))
                elif cell == 3:
                    pygame.draw.rect(screen, (255, 100, 255), (x, y, cell_size, cell_size))

    def _draw_food(self, screen: pygame.Surface, food_positions: set, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja dots (comida pequeña) CLARAMENTE VISIBLES."""
        # Radio: 30% del tamaño de celda (MUCHO más grande)
        dot_radius = max(4.5, int(cell_size * -9))
        
        for row, col in food_positions:
            center_x = offset_x + col * cell_size + cell_size // 2
            center_y = offset_y + row * cell_size + cell_size // 2
            
            # Círculo exterior blanco brillante
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), dot_radius)
            # Círculo interior amarillo (brillo)
            pygame.draw.circle(screen, (255, 255, 200), (center_x, center_y), max(2, dot_radius - 2))
    
    def _draw_food_fallback(self, screen: pygame.Surface, food_positions: set, offset_x: int, offset_y: int, cell_size: int, dot_size: int = 0) -> None:
        """Dibuja dots como círculos blancos brillantes (fallback)."""
        # Radio: 25% del tamaño de celda (más visible)
        dot_radius = max(4, cell_size // 4) if dot_size == 0 else dot_size // 2
        
        for row, col in food_positions:
            center_x = offset_x + col * cell_size + cell_size // 2
            center_y = offset_y + row * cell_size + cell_size // 2
            
            # Dibuja círculo blanco sólido
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), dot_radius)
            
            # Agrega brillo (círculo amarillo claro en el centro)
            pygame.draw.circle(screen, (255, 255, 200), (center_x, center_y), max(2, dot_radius - 1))

    def _draw_power_pellets(self, screen: pygame.Surface, pellet_positions: set, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja power pellets (manzanas) MÁS GRANDES Y VISIBLES."""
        # Tamaño: 60% del tamaño de celda (el doble que los dots)
        pellet_size = max(12, int(cell_size * 0.6))
        
        apple = self.sprites.get("apple")
        
        if apple and apple.get_width() > 0:
            try:
                apple_scaled = pygame.transform.scale(apple, (pellet_size, pellet_size))
                for row, col in pellet_positions:
                    x = offset_x + col * cell_size + (cell_size - pellet_size) // 2
                    y = offset_y + row * cell_size + (cell_size - pellet_size) // 2
                    screen.blit(apple_scaled, (x, y))
            except:
                # Fallback: círculo rojo grande
                for row, col in pellet_positions:
                    center_x = offset_x + col * cell_size + cell_size // 2
                    center_y = offset_y + row * cell_size + cell_size // 2
                    pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), pellet_size // 2)
                    pygame.draw.circle(screen, (255, 150, 150), (center_x, center_y), pellet_size // 3)
        else:
            # Fallback: círculo rojo grande
            for row, col in pellet_positions:
                center_x = offset_x + col * cell_size + cell_size // 2
                center_y = offset_y + row * cell_size + cell_size // 2
                pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), pellet_size // 2)
                pygame.draw.circle(screen, (255, 150, 150), (center_x, center_y), pellet_size // 3)

    def _draw_pacman(self, screen: pygame.Surface, pacman, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja Pac-Man con interpolación suave."""
        pacman_sprite = self._get_pacman_sprite(pacman.direction)
        pacman_scaled = pygame.transform.scale(pacman_sprite, (cell_size, cell_size))
        
        # Interpolar posición (maneja túneles automáticamente)
        target = tuple(pacman.position)
        smooth_row, smooth_col = self._interpolate_position(self.pacman_smooth_pos, target)
        
        # Calcular coordenadas en píxeles
        x = offset_x + int(smooth_col * cell_size)
        y = offset_y + int(smooth_row * cell_size)
        
        screen.blit(pacman_scaled, (x, y))

    def _draw_ghosts(self, screen: pygame.Surface, ghosts: list, offset_x: int, offset_y: int, cell_size: int) -> None:
        """Dibuja fantasmas con interpolación suave."""
        for ghost in ghosts:
            # Elegir sprite
            if ghost.is_vulnerable:
                sprite = self.sprites.get("blue_ghost")
            else:
                sprite = self.sprites.get(ghost.ghost_type)
            
            if not sprite:
                continue
            
            ghost_scaled = pygame.transform.scale(sprite, (cell_size, cell_size))
            
            # Transparencia si está en casa
            if ghost.in_house:
                ghost_scaled.set_alpha(128)
            else:
                ghost_scaled.set_alpha(255)
            
            # Inicializar posición suave si no existe
            ghost_id = id(ghost)
            if ghost_id not in self.ghost_smooth_pos:
                self.ghost_smooth_pos[ghost_id] = [float(ghost.position[0]), float(ghost.position[1])]
            
            # Resetear si el fantasma fue teletransportado (comido y respawneado)
            if hasattr(ghost, 'just_teleported') and ghost.just_teleported:
                self.ghost_smooth_pos[ghost_id] = [float(ghost.position[0]), float(ghost.position[1])]
                ghost.just_teleported = False
            
            # Interpolar posición (maneja respawns automáticamente)
            target = tuple(ghost.position)
            smooth_row, smooth_col = self._interpolate_position(self.ghost_smooth_pos[ghost_id], target)
            
            # Calcular coordenadas en píxeles
            x = offset_x + int(smooth_col * cell_size)
            y = offset_y + int(smooth_row * cell_size)
            
            screen.blit(ghost_scaled, (x, y))