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
BACKGROUND_COLOR = (0, 0, 0)
FPS_LIMIT = 60  # FPS fijos para evitar velocidad variable


def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()

    # Inicializar subsistemas
    sound_manager = SoundManager()
    game_core = GameCore(sound_manager)
    score_manager = ScoreManager()
    hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
    sprite_renderer = SpriteRenderer()

    # Cargar y reproducir música de fondo
    if sound_manager.load_music("background.ogg"):
        sound_manager.play_music()

    # Registrar callbacks del HUD
    def start_game():
        game_core.start_new_game()
        player_name = hud.get_player_name()
        print(f"[MAIN] {player_name} inició el juego - Nivel {game_core.level}")

    def quit_game():
        pygame.quit()
        sys.exit()

    def back_to_menu():
        game_core.game_state = GameState.MENU
        print("[MAIN] Volver al menú")

    hud.set_callbacks(start_game, quit_game, back_to_menu)

    # Variables de control
    running = True
    frame_count = 0

    # Bucle principal
    while running:
        frame_count += 1
        
        # --- PROCESAR EVENTOS ---
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
                    elif event.key == pygame.K_ESCAPE:
                        game_core.handle_input("PAUSE")
            
            elif game_core.is_paused():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_core.handle_input("PAUSE")
            
            elif game_core.is_game_over():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Guardar puntaje antes de reiniciar
                    if game_core.pacman and game_core.pacman.score > 0:
                        player_name = hud.get_player_name()
                        
                        # Siempre guardar el puntaje (no solo high scores)
                        score_manager.add_score(
                            score=game_core.pacman.score,
                            level=game_core.level,
                            name=player_name
                        )
                        
                        if score_manager.is_high_score(game_core.pacman.score):
                            print(f"[MAIN] ¡{player_name} logró un nuevo récord! {game_core.pacman.score} puntos")
                        else:
                            print(f"[MAIN] Partida guardada: {player_name} - {game_core.pacman.score} puntos")
                    
                    # Volver al menú para nuevo jugador
                    game_core.game_state = GameState.MENU
                    hud.reset_for_new_game()  # Opcional: limpia el nombre anterior

        # --- ACTUALIZAR LÓGICA ---
        if game_core.is_playing():
            game_core.update()

        # --- RENDERIZAR ---
        screen.fill(BACKGROUND_COLOR)

        # Renderizar mundo del juego
        if game_core.is_playing() or game_core.is_paused():
            sprite_renderer.draw_world(screen, game_core, cell_size=30)

        # Renderizar HUD (menús, puntajes, etc.)
        hud.draw(screen, game_core.game_state, game_core, score_manager)

        pygame.display.flip()

        # --- CONTROL DE FPS ---
        clock.tick(FPS_LIMIT)

        # Debug cada 60 frames (1 segundo)
        if frame_count % 60 == 0 and game_core.is_playing():
            player_name = hud.get_player_name()
            print(f"[DEBUG] {player_name} - Score: {game_core.pacman.score} | "
                  f"Vidas: {game_core.pacman.lives} | "
                  f"Comida: {len(game_core.food_positions)} | "
                  f"Fantasmas activos: {sum(1 for g in game_core.ghosts if not g.in_house)}")

    # Guardar puntaje final al cerrar el juego (si no se guardó antes)
    if game_core.pacman and game_core.pacman.score > 0 and game_core.is_game_over():
        player_name = hud.get_player_name()
        score_manager.add_score(
            score=game_core.pacman.score,
            level=game_core.level,
            name=player_name
        )
        print(f"[MAIN] Partida final guardada: {player_name} - {game_core.pacman.score} puntos")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()