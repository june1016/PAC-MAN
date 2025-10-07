"""
Módulo para la gestión de audio del juego: música de fondo y efectos de sonido.

Utiliza pygame.mixer para reproducir archivos de audio en formatos libres (.ogg, .wav).
Incluye sistema de aceleración progresiva de música según el nivel.
"""

import os
import pygame
from typing import Optional


class SoundManager:
    """
    Gestor centralizado de audio para el juego PACMAN.
    
    Maneja música de fondo y efectos de sonido con carga perezosa, manejo de errores
    y aceleración dinámica de música según nivel.
    """

    def __init__(self, assets_dir: str = "assets/audio"):
        """
        Inicializa el gestor de sonido.
        
        Args:
            assets_dir: Directorio donde se encuentran los archivos de audio.
        """
        self.assets_dir = assets_dir
        self.music_loaded = False
        self.music_paused = False
        self.current_level = 1
        self.base_volume = 0.6  # Volumen base de la música
        self.sounds = {}
        self._init_mixer()

    def _init_mixer(self) -> None:
        """Inicializa el mezclador de Pygame si no está activo."""
        if not pygame.mixer.get_init():
            try:
                # Configuración optimizada para efectos de pitch/velocidad
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                print("[AUDIO] Mixer inicializado correctamente")
            except pygame.error as e:
                print(f"[AUDIO] Error al inicializar mixer: {e}")

    def _load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """
        Carga un efecto de sonido de forma segura.
        
        Args:
            filename: Nombre del archivo (ej.: 'eat.wav').
            
        Returns:
            Objeto de sonido, o None si falla.
        """
        if not pygame.mixer.get_init():
            return None

        filepath = os.path.join(self.assets_dir, filename)
        if not os.path.exists(filepath):
            print(f"[AUDIO] No encontrado: {filepath}")
            return None

        try:
            return pygame.mixer.Sound(filepath)
        except pygame.error as e:
            print(f"[AUDIO] Error al cargar {filename}: {e}")
            return None

    def load_music(self, filename: str = "background.ogg") -> bool:
        """
        Carga la música de fondo.
        
        Args:
            filename: Nombre del archivo de música.
            
        Returns:
            True si se cargó correctamente.
        """
        if not pygame.mixer.get_init():
            self.music_loaded = False
            return False

        filepath = os.path.join(self.assets_dir, filename)
        if not os.path.exists(filepath):
            print(f"[AUDIO] Música no encontrada: {filepath}")
            self.music_loaded = False
            return False

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.base_volume)
            self.music_loaded = True
            print(f"[AUDIO] Música cargada: {filename}")
            return True
        except pygame.error as e:
            print(f"[AUDIO] Error al cargar música: {e}")
            self.music_loaded = False
            return False

    def play_music(self, loops: int = -1) -> None:
        """
        Reproduce la música de fondo en loop.
        
        Args:
            loops: Número de repeticiones (-1 = infinito).
        """
        if self.music_loaded and pygame.mixer.get_init():
            pygame.mixer.music.play(loops=loops)
            self.music_paused = False
            print("[AUDIO] Música reproduciendo")

    def pause_music(self) -> None:
        """Pausa la música de fondo."""
        if pygame.mixer.get_init() and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True
            print("[AUDIO] Música pausada")

    def resume_music(self) -> None:
        """Reanuda la música de fondo."""
        if pygame.mixer.get_init() and self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
            print("[AUDIO] Música reanudada")

    def stop_music(self) -> None:
        """Detiene la música de fondo."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            self.music_paused = False
            print("[AUDIO] Música detenida")

    def set_level_intensity(self, level: int) -> None:
        """
        Ajusta la intensidad de la música según el nivel.
        Aumenta el volumen progresivamente para simular aceleración.
        
        Args:
            level: Nivel actual del juego (1, 2, 3, ...)
        """
        if not pygame.mixer.get_init() or not self.music_loaded:
            return
        
        self.current_level = level
        
        # Fórmula de escalado: +5% de volumen por nivel (máximo 100%)
        volume_boost = (level - 1) * 0.05
        new_volume = min(1.0, self.base_volume + volume_boost)
        
        pygame.mixer.music.set_volume(new_volume)
        
        print(f"[AUDIO] Nivel {level} - Volumen ajustado a {new_volume:.2f}")
        
        # Nota: Pygame no soporta cambiar pitch/velocidad directamente
        # Para un efecto más dramático, considera estos métodos adicionales:
        # 1. Tener múltiples versiones del audio (slow, normal, fast)
        # 2. Usar una biblioteca externa como pydub o librosa
        # 3. Pre-procesar el audio en diferentes velocidades

    def get_intensity_message(self, level: int) -> str:
        """
        Devuelve un mensaje descriptivo de la intensidad del nivel.
        
        Args:
            level: Nivel actual
            
        Returns:
            Mensaje descriptivo
        """
        if level <= 2:
            return "🎵 Calma"
        elif level <= 4:
            return "🎶 Ritmo Normal"
        elif level <= 6:
            return "🎸 Intensificando"
        elif level <= 8:
            return "🔥 Frenético"
        else:
            return "⚡ MÁXIMA VELOCIDAD"

    def play_eat_sound(self) -> None:
        """Reproduce el sonido al recolectar comida."""
        self._play_sound("eat.wav", volume=0.4)

    def play_death_sound(self) -> None:
        """Reproduce el sonido al perder una vida."""
        self._play_sound("death.wav", volume=0.7)

    def play_level_start_sound(self) -> None:
        """Reproduce un sonido al iniciar un nivel."""
        self._play_sound("start.wav", volume=0.5)

    def _play_sound(self, filename: str, volume: float = 0.5) -> None:
        """
        Reproduce un efecto de sonido (carga perezosa).
        
        Args:
            filename: Nombre del archivo de sonido.
            volume: Volumen del efecto (0.0 a 1.0)
        """
        if not pygame.mixer.get_init():
            return

        # Carga perezosa
        if filename not in self.sounds:
            sound = self._load_sound(filename)
            if sound:
                self.sounds[filename] = sound
            else:
                self.sounds[filename] = None

        sound = self.sounds[filename]
        if sound:
            sound.set_volume(volume)
            sound.play()