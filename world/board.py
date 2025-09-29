# world/board.py
"""
Generador de tableros tipo Pac-Man Maze.
Mapa fijo inspirado en el diseño clásico con casa de fantasmas.
"""

# Constantes del tablero
DEFAULT_ROWS = 19
DEFAULT_COLS = 21
WALL = 1
PATH = 0
GHOST_HOUSE = 2  # Celda especial para la casa de fantasmas (solo fantasmas pueden estar aquí)

# Mapa Pac-Man auténtico 19x21
# 0 = Camino, 1 = Pared, 2 = Casa de fantasmas
ORIGINAL_PACMAN_MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 2, 2, 2, 1, 1, 0, 1, 0, 1, 1, 1, 1],  # Casa fantasmas
    [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0],  # Puerta casa
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
]

# Posiciones de spawn (fila, columna)
PACMAN_SPAWN = (16, 10)  # Parte inferior cerca del centro
GHOST_HOUSE_CENTER = (10, 10)  # Centro de la casa de fantasmas
GHOST_SPAWN = [
    (10, 9),   # Blinky
    (10, 10),  # Pinky (centro)
    (10, 11),  # Inky
    (9, 10)    # Clyde
]
GHOST_HOUSE_EXIT = (8, 10)  # Posición justo fuera de la casa
POWER_PELLET_POSITIONS = [(1, 1), (1, 19), (16, 1), (16, 19)]  # Esquinas estratégicas


class BoardGenerator:
    """Generador del laberinto tipo Pac-Man Maze."""

    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS):
        if rows != DEFAULT_ROWS or cols != DEFAULT_COLS:
            print(f"[WARN] Mapa fijo {DEFAULT_ROWS}x{DEFAULT_COLS}. Dimensiones ({rows}x{cols}) ignoradas.")
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS

    def generate_maze(self) -> list[list[int]]:
        """Devuelve el mapa fijo de Pac-Man."""
        return [row[:] for row in ORIGINAL_PACMAN_MAZE]

    def get_walkable_positions(self, maze: list[list[int]]) -> list[tuple[int, int]]:
        """Extrae posiciones transitables (PATH=0)."""
        walkable = []
        for i in range(self.rows):
            for j in range(self.cols):
                if maze[i][j] == PATH:
                    walkable.append((i, j))
        return walkable

    def place_food(
        self,
        walkable_positions: list[tuple[int, int]],
        num_food: int,
        exclude_positions: set[tuple[int, int]] = None
    ) -> set[tuple[int, int]]:
        """
        Coloca comida aleatoriamente usando PRNG (Mersenne Twister).
        
        Args:
            walkable_positions: Celdas transitables
            num_food: Cantidad de comida
            exclude_positions: Posiciones a excluir (spawns, power-ups)
        
        Returns:
            Set de posiciones con comida
        """
        if exclude_positions is None:
            exclude_positions = set()

        valid_positions = [pos for pos in walkable_positions if pos not in exclude_positions]

        if num_food > len(valid_positions):
            num_food = len(valid_positions)

        import random
        food_positions = set(random.sample(valid_positions, num_food))
        return food_positions