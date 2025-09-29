"""
Módulo para la gestión persistente de puntajes, ranking y logros.

Almacena el top 10 de puntajes en un archivo JSON, permitiendo que los
jugadores comparen su desempeño a lo largo del tiempo.
"""

import os
import json
from typing import List, Dict


class ScoreManager:
    """
    Gestor de puntajes y ranking del juego.
    
    Almacena y recupera los mejores puntajes en un archivo JSON.
    """

    def __init__(self, data_file: str = "data/scores.json"):
        """
        Inicializa el gestor y carga los puntajes existentes.
        
        Args:
            data_file (str): Ruta al archivo JSON de puntajes.
        """
        self.data_file = data_file
        self._ensure_data_dir()
        self.scores = self._load_scores()

    def _ensure_data_dir(self) -> None:
        """Crea el directorio de datos si no existe."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def _load_scores(self) -> List[Dict[str, int]]:
        """
        Carga los puntajes desde el archivo JSON.
        
        Returns:
            List[Dict]: Lista de puntajes (cada uno con 'score', 'level', 'name').
        """
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Validar estructura
                if isinstance(data, list):
                    return [entry for entry in data if self._is_valid_entry(entry)]
                return []
        except (json.JSONDecodeError, IOError):
            return []

    def _is_valid_entry(self, entry) -> bool:
        """Verifica que una entrada tenga los campos necesarios."""
        return (
            isinstance(entry, dict)
            and "score" in entry
            and "level" in entry
            and "name" in entry
            and isinstance(entry["score"], int)
            and isinstance(entry["level"], int)
            and isinstance(entry["name"], str)
        )

    def add_score(self, score: int, level: int, name: str = "Player") -> bool:
        """
        Agrega un nuevo puntaje al ranking si entra en el top 10.
        
        Args:
            score (int): Puntaje total del jugador.
            level (int): Nivel alcanzado.
            name (str): Nombre del jugador.
            
        Returns:
            bool: True si el puntaje entró en el ranking.
        """
        new_entry = {"score": score, "level": level, "name": name}
        self.scores.append(new_entry)
        # Ordenar por puntaje descendente y mantener solo top 10
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]
        self._save_scores()
        return new_entry in self.scores

    def get_top_scores(self, n: int = 10) -> List[Dict[str, int]]:
        """
        Devuelve los primeros 'n' puntajes del ranking.
        
        Args:
            n (int): Cantidad de puntajes a devolver.
            
        Returns:
            List[Dict]: Lista de entradas del ranking.
        """
        return self.scores[:n]

    def _save_scores(self) -> None:
        """Guarda los puntajes actuales en el archivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2)
        except IOError:
            # Silenciosamente ignora errores de escritura (ej.: permisos)
            pass

    def is_high_score(self, score: int) -> bool:
        """
        Verifica si un puntaje califica para el ranking actual.
        
        Args:
            score (int): Puntaje a evaluar.
            
        Returns:
            bool: True si entra en el top 10.
        """
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]["score"]