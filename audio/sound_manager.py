"""
Módulo para la gestión de audio del juego: música de fondo y efectos de sonido.

Utiliza pygame.mixer para reproducir archivos de audio en formatos libres (.ogg, .wav).
El módulo es tolerante a la ausencia de archivos: si no se encuentran, el juego continúa en silencio.
"""

import os
import pygame
from typing import Optional


class SoundManager:
    """
    Gestor centralizado de audio para el juego PACMAN.
    
    Maneja música de fondo y efectos de sonido con carga perezosa y manejo de errores.
    """

    def __init__(self, assets_dir: str = "assets/audio"):
        """
        Inicializa el gestor de sonido.
        
        Args:
            assets_dir (str): Directorio donde se encuentran los archivos de audio.
        """
        self.assets_dir = assets_dir
        self.music_loaded = False
        self.sounds = {}
        self._init_mixer()

    def _init_mixer(self) -> None:
        """Inicializa el mezclador de Pygame si no está activo."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            except pygame.error:
                # Si falla (ej.: en entornos sin audio), se silencia
                pass

    def _load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """
        Carga un efecto de sonido de forma segura.
        
        Args:
            filename (str): Nombre del archivo (ej.: 'eat.wav').
            
        Returns:
            Optional[pygame.mixer.Sound]: Objeto de sonido, o None si falla.
        """
        if not pygame.mixer.get_init():
            return None

        filepath = os.path.join(self.assets_dir, filename)
        if not os.path.exists(filepath):
            return None

        try:
            return pygame.mixer.Sound(filepath)
        except pygame.error:
            return None

    def load_music(self, filename: str = "background.ogg") -> bool:
        """
        Carga la música de fondo.
        
        Args:
            filename (str): Nombre del archivo de música.
            
        Returns:
            bool: True si se cargó correctamente.
        """
        if not pygame.mixer.get_init():
            self.music_loaded = False
            return False

        filepath = os.path.join(self.assets_dir, filename)
        if not os.path.exists(filepath):
            self.music_loaded = False
            return False

        try:
            pygame.mixer.music.load(filepath)
            self.music_loaded = True
            return True
        except pygame.error:
            self.music_loaded = False
            return False

    def play_music(self, loops: int = -1) -> None:
        """
        Reproduce la música de fondo en loop.
        
        Args:
            loops (int): Número de repeticiones (-1 = infinito).
        """
        if self.music_loaded and pygame.mixer.get_init():
            pygame.mixer.music.play(loops=loops)

    def stop_music(self) -> None:
        """Detiene la música de fondo."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def play_eat_sound(self) -> None:
        """Reproduce el sonido al recolectar comida."""
        self._play_sound("eat.wav")

    def play_death_sound(self) -> None:
        """Reproduce el sonido al perder una vida."""
        self._play_sound("death.wav")

    def play_level_start_sound(self) -> None:
        """Reproduce un sonido al iniciar un nivel."""
        self._play_sound("start.wav")

    def _play_sound(self, filename: str) -> None:
        """
        Reproduce un efecto de sonido (carga perezosa).
        
        Args:
            filename (str): Nombre del archivo de sonido.
        """
        if not pygame.mixer.get_init():
            return

        if filename not in self.sounds:
            sound = self._load_sound(filename)
            if sound:
                # Ajustar volumen para efectos (menos que la música)
                sound.set_volume(0.5)
                self.sounds[filename] = sound
            else:
                self.sounds[filename] = None

        sound = self.sounds[filename]
        if sound:
            sound.play()