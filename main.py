"""
Punto de entrada principal del juego PACMAN.

Inicializa Pygame, orquesta todos los módulos y ejecuta el bucle principal.
"""

import pygame
import sys
from core.game import GameCore, GameState
from audio.sound_manager import SoundManager
from data.score_manager import ScoreManager
from ui.hud import HUD
from ui.sprite_renderer import SpriteRenderer


# Configuración de la ventana
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "PACMAN - Proyecto Académico"
BACKGROUND_COLOR = (0, 0, 0)  # Negro


def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()

    # Inicializar subsistemas
    sound_manager = SoundManager()  # Inicializar sound_manager aquí
    game_core = GameCore(sound_manager) # Pasar sound_manager a GameCore
    score_manager = ScoreManager()
    hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
    sprite_renderer = SpriteRenderer()  # ✅ Inicializado una vez

    # Cargar y reproducir música de fondo
    if sound_manager.load_music("background.ogg"):
        sound_manager.play_music()

    # Registrar callbacks del HUD
    def start_game():
        game_core.start_new_game()
        print("Game started. State:", game_core.game_state)
        sound_manager.play_level_start_sound()

    def quit_game():
        pygame.quit()
        sys.exit()

    def back_to_menu():
        game_core.game_state = GameState.MENU

    hud.set_callbacks(start_game, quit_game, back_to_menu)

    # Bucle principal
    running = True
    while running:
        # --- Procesar eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Eventos de UI (menú, botones)
            hud.handle_event(event)

            # Eventos de juego
            if game_core.is_playing():
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game_core.handle_input("UP")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game_core.handle_input("DOWN")
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        game_core.handle_input("LEFT")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game_core.handle_input("RIGHT")
                    elif event.key == pygame.K_ESCAPE:  # Pausar el juego
                        game_core.game_state = GameState.PAUSED
            elif game_core.game_state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Reanudar el juego
                    game_core.game_state = GameState.PLAYING
            elif game_core.is_game_over():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    start_game()

        # --- Actualizar lógica del juego ---
        if game_core.is_playing():
            prev_score = game_core.pacman.score
            game_core.update()
            # Reproducir sonido de comida solo si el puntaje aumentó
            if game_core.pacman.score > prev_score:
                sound_manager.play_eat_sound()
            # Reproducir sonido de muerte si se perdió una vida
            if game_core.pacman.lives < getattr(game_core, '_last_lives', 3):
                sound_manager.play_death_sound()
            game_core._last_lives = game_core.pacman.lives

        # --- Renderizar ---
        screen.fill(BACKGROUND_COLOR)

        print("Game state:", game_core.game_state, "Is playing:", game_core.is_playing())

        # --- Renderizado del mundo ---
        if game_core.is_playing():
            sprite_renderer.draw_world(screen, game_core, cell_size=32)  # ✅ Usar instancia existente

        hud.draw(screen, game_core.game_state, game_core, score_manager)
        pygame.display.flip()

        # --- Control de FPS ---
        fps = game_core.get_fps() if game_core.is_playing() else 60
        clock.tick(fps)

    # Guardar puntaje final si aplica
    if game_core.pacman and game_core.pacman.score > 0:
        if score_manager.is_high_score(game_core.pacman.score):
            score_manager.add_score(
                score=game_core.pacman.score,
                level=game_core.level,
                name="Player"
            )

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()