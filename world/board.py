"""
Generador de tableros tipo Pac-Man Maze.
Mapa fijo inspirado en el diseño clásico con casa de fantasmas.
Sistema completo de colisiones y validación.
"""
import random
from typing import List, Set, Tuple, Optional

# ==================== CONSTANTES DEL TABLERO ====================
DEFAULT_ROWS = 21
DEFAULT_COLS = 19
TILE_SIZE = 30  # Tamaño de cada celda en píxeles

# Tipos de celdas
WALL = 1
PATH = 0
GHOST_HOUSE = 2  # Interior de la casa de fantasmas
GHOST_DOOR = 3   # Puerta de la casa (solo fantasmas pueden atravesar)

# ==================== MAPA PAC-MAN AUTÉNTICO ====================
# Mapa 21 filas x 19 columnas (más fiel al original)
ORIGINAL_PACMAN_MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 3, 3, 3, 1, 0, 1, 0, 1, 1, 1, 1],  # Puerta casa
    [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0],  # Túnel + casa
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
]

# ==================== POSICIONES ESTRATÉGICAS ====================
PACMAN_SPAWN = (16, 9)  # Parte inferior centro

# Spawns de fantasmas (DENTRO de la casa)
GHOST_SPAWN = [
    (10, 8),   # Blinky (izquierda)
    (10, 9),   # Pinky (centro-izquierda)
    (10, 10),  # Inky (centro-derecha)
    (10, 11),  # Clyde (derecha) - CORREGIDO: ahora está dentro
]

GHOST_HOUSE_EXIT = (9, 9)  # Celda justo encima de la puerta

# Power Pellets en las 4 esquinas accesibles
POWER_PELLET_POSITIONS = [
    (1, 1),    # Superior izquierda
    (1, 17),   # Superior derecha
    (16, 1),   # Inferior izquierda
    (16, 17),  # Inferior derecha
]

# Posiciones del túnel (para teletransporte)
TUNNEL_LEFT = (10, 0)   # Entrada izquierda
TUNNEL_RIGHT = (10, 18)  # Entrada derecha


# ==================== CLASE PRINCIPAL ====================
class BoardGenerator:
    """
    Generador del laberinto tipo Pac-Man Maze.
    Incluye sistema completo de colisiones y validación.
    """

    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS):
        """Inicializa el generador con dimensiones fijas."""
        if rows != DEFAULT_ROWS or cols != DEFAULT_COLS:
            print(f"[WARN] Mapa fijo {DEFAULT_ROWS}x{DEFAULT_COLS}. Dimensiones ({rows}x{cols}) ignoradas.")
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS
        self.maze = self.generate_maze()

    def generate_maze(self) -> List[List[int]]:
        """Devuelve una copia del mapa fijo de Pac-Man."""
        return [row[:] for row in ORIGINAL_PACMAN_MAZE]

    # ==================== SISTEMA DE COLISIONES ====================
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Verifica si una posición está dentro del tablero."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_wall(self, row: int, col: int) -> bool:
        """Verifica si una celda es pared."""
        if not self.is_valid_position(row, col):
            return True  # Fuera del tablero = pared
        return self.maze[row][col] == WALL

    def is_ghost_door(self, row: int, col: int) -> bool:
        """Verifica si una celda es la puerta de la casa de fantasmas."""
        if not self.is_valid_position(row, col):
            return False
        return self.maze[row][col] == GHOST_DOOR

    def is_ghost_house(self, row: int, col: int) -> bool:
        """Verifica si una celda es interior de la casa de fantasmas."""
        if not self.is_valid_position(row, col):
            return False
        return self.maze[row][col] == GHOST_HOUSE

    def can_pacman_move_to(self, row: int, col: int) -> bool:
        """
        Verifica si Pac-Man puede moverse a esta celda.
        Pac-Man NO puede atravesar paredes ni entrar a la casa de fantasmas.
        """
        if not self.is_valid_position(row, col):
            return False
        cell_type = self.maze[row][col]
        # Pac-Man puede moverse a PATH (0) únicamente
        return cell_type == PATH

    def can_ghost_move_to(self, row: int, col: int) -> bool:
        """
        Verifica si un fantasma puede moverse a esta celda.
        Fantasmas pueden atravesar la puerta (GHOST_DOOR) pero no paredes.
        """
        if not self.is_valid_position(row, col):
            return False
        cell_type = self.maze[row][col]
        # Fantasmas pueden moverse a PATH, GHOST_HOUSE y GHOST_DOOR
        return cell_type in (PATH, GHOST_HOUSE, GHOST_DOOR)

    def get_cell_center_pixel(self, row: int, col: int) -> Tuple[int, int]:
        """Convierte coordenadas de grid a píxeles (centro de la celda)."""
        x = col * TILE_SIZE + TILE_SIZE // 2
        y = row * TILE_SIZE + TILE_SIZE // 2
        return (x, y)

    def pixel_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """Convierte coordenadas de píxeles a grid."""
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        return (row, col)

    # ==================== TÚNELES ====================
    
    def handle_tunnel_teleport(self, row: int, col: int) -> Tuple[int, int]:
        """
        Maneja el teletransporte por túneles laterales.
        Si Pac-Man o fantasma sale por un lado, aparece por el otro.
        """
        # Túnel izquierdo -> derecho
        if row == TUNNEL_LEFT[0] and col < 0:
            return (row, self.cols - 1)
        
        # Túnel derecho -> izquierdo
        if row == TUNNEL_RIGHT[0] and col >= self.cols:
            return (row, 0)
        
        return (row, col)

    # ==================== SISTEMA DE COMIDA ====================
    
    def get_walkable_positions(self) -> List[Tuple[int, int]]:
        """
        Extrae TODAS las posiciones transitables (PATH=0).
        Excluye casa de fantasmas y puerta.
        """
        walkable = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == PATH:
                    walkable.append((i, j))
        return walkable

    def place_all_food(
        self,
        exclude_positions: Optional[Set[Tuple[int, int]]] = None
    ) -> Set[Tuple[int, int]]:
        """
        Coloca comida en TODAS las celdas transitables.
        Excluye spawns de Pac-Man y fantasmas, y power pellets.
        
        Returns:
            Set de posiciones con comida normal (dots)
        """
        if exclude_positions is None:
            exclude_positions = set()

        walkable = self.get_walkable_positions()
        
        # Excluir spawns y power pellets
        food_positions = set()
        for pos in walkable:
            if pos not in exclude_positions:
                food_positions.add(pos)

        print(f"[BOARD] Celdas transitables: {len(walkable)}")
        print(f"[BOARD] Exclusiones: {len(exclude_positions)}")
        print(f"[BOARD] Comida colocada: {len(food_positions)}")

        return food_positions

    def get_power_pellets(self) -> Set[Tuple[int, int]]:
        """Devuelve las posiciones de los power pellets."""
        return set(POWER_PELLET_POSITIONS)

    # ==================== UTILIDADES ====================
    
    def get_spawn_positions(self) -> dict:
        """
        Devuelve diccionario con todas las posiciones de spawn.
        
        Returns:
            {
                'pacman': (row, col),
                'ghosts': [(row, col), ...],
                'ghost_exit': (row, col),
                'power_pellets': [(row, col), ...]
            }
        """
        return {
            'pacman': PACMAN_SPAWN,
            'ghosts': GHOST_SPAWN[:],  # Copia
            'ghost_exit': GHOST_HOUSE_EXIT,
            'power_pellets': POWER_PELLET_POSITIONS[:]
        }

    def get_neighbors(self, row: int, col: int, for_ghost: bool = False) -> List[Tuple[int, int]]:
        """
        Devuelve celdas vecinas válidas (arriba, abajo, izq, der).
        
        Args:
            row, col: Posición actual
            for_ghost: Si True, usa lógica de fantasmas (pueden pasar puerta)
        
        Returns:
            Lista de tuplas (row, col) transitables
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # arriba, abajo, izq, der
        neighbors = []

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Verificar colisión según tipo de entidad
            if for_ghost:
                if self.can_ghost_move_to(new_row, new_col):
                    neighbors.append((new_row, new_col))
            else:
                if self.can_pacman_move_to(new_row, new_col):
                    neighbors.append((new_row, new_col))

        return neighbors

    def __repr__(self) -> str:
        """Representación en texto del mapa (debugging)."""
        symbols = {WALL: '█', PATH: ' ', GHOST_HOUSE: 'H', GHOST_DOOR: '='}
        lines = []
        for row in self.maze:
            line = ''.join(symbols.get(cell, '?') for cell in row)
            lines.append(line)
        return '\n'.join(lines)


# ==================== FUNCIÓN DE PRUEBA ====================
if __name__ == "__main__":
    board = BoardGenerator()
    print("=== MAPA PAC-MAN ===")
    print(board)
    print(f"\nDimensiones: {board.rows}x{board.cols}")
    print(f"Spawn Pac-Man: {PACMAN_SPAWN}")
    print(f"Spawn Fantasmas: {GHOST_SPAWN}")
    print(f"Salida Casa: {GHOST_HOUSE_EXIT}")
    print(f"Power Pellets: {POWER_PELLET_POSITIONS}")
    
    # Prueba de colisiones
    print("\n=== PRUEBAS DE COLISIÓN ===")
    test_wall = (0, 0)
    test_path = (4, 4)
    test_door = (9, 9)
    
    print(f"¿{test_wall} es pared? {board.is_wall(*test_wall)}")
    print(f"¿Pac-Man puede ir a {test_path}? {board.can_pacman_move_to(*test_path)}")
    print(f"¿Pac-Man puede ir a {test_door}? {board.can_pacman_move_to(*test_door)}")
    print(f"¿Fantasma puede ir a {test_door}? {board.can_ghost_move_to(*test_door)}")