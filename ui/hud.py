"""
Módulo de interfaz de usuario: menús, HUD y visualización de ranking.

Renderiza texto, botones y elementos gráficos usando Pygame.
"""

import pygame
from typing import Callable  # ✅ Importar Callable
from core.game import GameState


# Constantes de estilo
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
TEXT_COLOR = (255, 255, 0)      # Amarillo PACMAN
HIGHLIGHT_COLOR = (255, 100, 100)  # Rojo suave para resaltar
BACKGROUND_COLOR = (0, 0, 0)    # Negro
BUTTON_COLOR = (50, 50, 150)
BUTTON_HOVER_COLOR = (100, 100, 255)


class Button:
    """Representa un botón interactivo en la interfaz."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback: Callable):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Dibuja el botón en la pantalla."""
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        """Actualiza el estado de hover según la posición del mouse."""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Maneja eventos de clic."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()


class HUD:
    """
    Sistema de visualización de información del juego (HUD) y menús.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont("Arial", FONT_SIZE_LARGE, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.SysFont("Courier New", FONT_SIZE_SMALL)

        # Botones del menú principal
        button_width, button_height = 200, 50
        center_x = screen_width // 2 - button_width // 2
        self.main_menu_buttons = [
            Button(center_x, 250, button_width, button_height, "Jugar", self._on_play),
            Button(center_x, 320, button_width, button_height, "Ranking", self._on_ranking),
            Button(center_x, 390, button_width, button_height, "Salir", self._on_quit),
        ]
        self.back_button = Button(20, 20, 100, 40, "Atrás", self._on_back)

        # Estados internos
        self.show_ranking = False
        self.callbacks = {
            "play": None,
            "quit": None,
            "back_to_menu": None,
        }

    def set_callbacks(self, play_callback: Callable, quit_callback: Callable, back_callback: Callable) -> None:  # ✅ Ahora Callable está definido
        """Registra callbacks para acciones del menú."""
        self.callbacks["play"] = play_callback
        self.callbacks["quit"] = quit_callback
        self.callbacks["back_to_menu"] = back_callback

    def _on_play(self) -> None:
        if self.callbacks["play"]:
            self.callbacks["play"]()

    def _on_ranking(self) -> None:
        """Mostrar la pantalla de ranking."""
        self.show_ranking = True

    def _on_quit(self) -> None:
        if self.callbacks["quit"]:
            self.callbacks["quit"]()

    def _on_back(self) -> None:
        self.show_ranking = False
        if self.callbacks["back_to_menu"]:
            self.callbacks["back_to_menu"]()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Procesa eventos de UI (clics, hover)."""
        mouse_pos = pygame.mouse.get_pos()
        if self.show_ranking:
            self.back_button.check_hover(mouse_pos)
            self.back_button.handle_event(event)
        else:
            for button in self.main_menu_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)

    def draw(self, screen: pygame.Surface, game_state: str, game_core=None, score_manager=None) -> None:
        """
        Renderiza la interfaz según el estado del juego.
        
        Args:
            screen (pygame.Surface): Superficie de Pygame para dibujar.
            game_state (str): Estado actual del juego.
            game_core (GameCore, opcional): Datos del juego en curso.
            score_manager (ScoreManager, opcional): Datos del ranking.
        """

        if game_state == GameState.PAUSED:
            self._draw_pause(screen)
        elif self.show_ranking:
            self._draw_ranking(screen, score_manager)
            self.back_button.draw(screen, self.font_small)
        elif game_state == GameState.MENU:
            self._draw_main_menu(screen)
        elif game_state == GameState.PLAYING and game_core:
            self._draw_hud(screen, game_core)
        elif game_state == GameState.GAME_OVER and game_core:
            self._draw_game_over(screen, game_core)

    def _draw_main_menu(self, screen: pygame.Surface) -> None:
        """Dibuja la pantalla principal del menú."""
        title = self.font_large.render("PACMAN", True, TEXT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))
        for button in self.main_menu_buttons:
            button.draw(screen, self.font_medium)

    def _draw_hud(self, screen: pygame.Surface, game_core) -> None:
        """Dibuja la interfaz durante el juego."""
        # Puntaje
        score_text = self.font_medium.render(f"Puntos: {game_core.pacman.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))

        # Nivel
        level_text = self.font_medium.render(f"Nivel: {game_core.level}", True, TEXT_COLOR)
        screen.blit(level_text, (20, 60))

        # Vidas
        lives_text = self.font_medium.render(f"Vidas: {game_core.pacman.lives}", True, TEXT_COLOR)
        screen.blit(lives_text, (20, 100))

        # Progreso
        progress = game_core.get_progress_percentage()
        progress_text = self.font_small.render(f"Avance: {progress:.1f}%", True, (100, 255, 100))
        screen.blit(progress_text, (20, 140))

    def _draw_pause(self, screen: pygame.Surface) -> None:
        """Dibuja la pantalla de pausa."""
        title = self.font_large.render("PAUSA", True, TEXT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 150))

        resume = self.font_medium.render("Presiona ESC para reanudar", True, (200, 200, 200))
        screen.blit(resume, (self.screen_width // 2 - resume.get_width() // 2, 300))

    def _draw_game_over(self, screen: pygame.Surface, game_core) -> None:
        """Dibuja la pantalla de fin del juego."""
        title = self.font_large.render("GAME OVER", True, HIGHLIGHT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 150))

        score = self.font_medium.render(f"Puntaje Final: {game_core.pacman.score}", True, TEXT_COLOR)
        screen.blit(score, (self.screen_width // 2 - score.get_width() // 2, 250))

        level = self.font_medium.render(f"Nivel Alcanzado: {game_core.level}", True, TEXT_COLOR)
        screen.blit(level, (self.screen_width // 2 - level.get_width() // 2, 300))

        restart = self.font_small.render("Presiona ESPACIO para reiniciar", True, (200, 200, 200))
        screen.blit(restart, (self.screen_width // 2 - restart.get_width() // 2, 400))

    def _draw_ranking(self, screen: pygame.Surface, score_manager) -> None:
        """Dibuja la pantalla de ranking."""
        title = self.font_large.render("RANKING", True, TEXT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))

        if not score_manager or not score_manager.scores:
            empty = self.font_medium.render("Sin puntajes aún", True, (150, 150, 150))
            screen.blit(empty, (self.screen_width // 2 - empty.get_width() // 2, 150))
            return

        y_offset = 150
        for i, entry in enumerate(score_manager.get_top_scores(10), 1):
            line = f"{i}. {entry['name']} - {entry['score']} pts (Nivel {entry['level']})"
            color = HIGHLIGHT_COLOR if i == 1 else TEXT_COLOR
            text = self.font_medium.render(line, True, color)
            screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, y_offset))
            y_offset += 40