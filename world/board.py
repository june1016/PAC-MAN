# world/board.py

"""
Módulo para la generación de tableros de juego (laberintos).
Ahora incluye un mapa fijo basado en el original de Pac-Man.
"""

# Constantes del tablero
DEFAULT_ROWS = 21
DEFAULT_COLS = 21
WALL = 1
PATH = 0

# Mapa original de Pac-Man (simplificado a 21x21)
# 1 = Pared, 0 = Camino
ORIGINAL_PACMAN_MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Posiciones de spawn (fila, columna)
PACMAN_SPAWN = (19, 10) # Centro inferior
GHOST_SPAWN = [(9, 9), (9, 10), (9, 11), (10, 10)] # Casa de fantasmas (centro)
POWER_PELLET_POSITIONS = [(1, 1), (1, 19), (19, 1), (19, 19)] # Esquinas


class BoardGenerator:
    """
    Generador de laberintos para el juego PACMAN.
    Ahora carga un mapa fijo basado en el original.
    """

    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS):
        """
        Inicializa el generador con dimensiones específicas.
        No se usan rows y cols porque el mapa es fijo.
        """
        if rows != DEFAULT_ROWS or cols != DEFAULT_COLS:
             print(f"Advertencia: El mapa es fijo de {DEFAULT_ROWS}x{DEFAULT_COLS}. Las dimensiones solicitadas ({rows}x{cols}) se ignoran.")
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS

    def generate_maze(self) -> list[list[int]]:
        """
        Devuelve el mapa fijo original de Pac-Man.

        Returns:
            List[List[int]]: Matriz 2D donde 1 = pared, 0 = camino.
        """
        # Devolvemos una copia para evitar modificaciones accidentales
        return [row[:] for row in ORIGINAL_PACMAN_MAZE]

    def get_walkable_positions(self, maze: list[list[int]]) -> list[tuple[int, int]]:
        """
        Extrae todas las posiciones transitables de un laberinto.

        Args:
            maze (List[List[int]]): Laberinto generado.

        Returns:
            List[Tuple[int, int]]: Lista de coordenadas (fila, columna) transitables.
        """
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
        Coloca comida de forma aleatoria en posiciones transitables.

        Usa el PRNG de Python (Mersenne Twister) para garantizar aleatoriedad controlada.

        Args:
            walkable_positions (List[Tuple[int, int]]): Lista de celdas donde se puede caminar.
            num_food (int): Cantidad de comida a colocar.
            exclude_positions (Set[Tuple[int, int]], opcional): Posiciones a excluir (ej.: spawn del jugador).

        Returns:
            Set[Tuple[int, int]]: Conjunto de posiciones donde se colocó comida.
        """
        if exclude_positions is None:
            exclude_positions = set()

        # Filtrar posiciones válidas
        valid_positions = [
            pos for pos in walkable_positions
            if pos not in exclude_positions
        ]

        if num_food > len(valid_positions):
            num_food = len(valid_positions)  # Evitar error si no hay suficientes celdas

        # Selección aleatoria sin reemplazo
        import random # Importar aquí para evitar dependencia global
        food_positions = set(random.sample(valid_positions, num_food))
        return food_positions

# --- Fin de board.py ---