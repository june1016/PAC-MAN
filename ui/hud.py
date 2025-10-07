"""
Módulo de interfaz de usuario: menús, HUD y visualización de ranking.
Incluye sistema de ingreso de nombre de jugador.
"""

import pygame
from typing import Callable
from core.game import GameState


# Constantes de estilo
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
TEXT_COLOR = (255, 255, 0)      # Amarillo PACMAN
HIGHLIGHT_COLOR = (255, 100, 100)  # Rojo suave
BACKGROUND_COLOR = (0, 0, 0)
BUTTON_COLOR = (50, 50, 150)
BUTTON_HOVER_COLOR = (100, 100, 255)
INPUT_BOX_COLOR = (50, 50, 50)
INPUT_BOX_ACTIVE_COLOR = (100, 100, 100)


class Button:
    """Representa un botón interactivo en la interfaz."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback: Callable):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.enabled = True

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Dibuja el botón en la pantalla."""
        if not self.enabled:
            color = (30, 30, 30)
            text_color = (100, 100, 100)
        else:
            color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
            text_color = TEXT_COLOR
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        """Actualiza el estado de hover según la posición del mouse."""
        if self.enabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Maneja eventos de clic."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.enabled:
                self.callback()


class InputBox:
    """Cuadro de texto para ingresar el nombre del jugador."""
    
    def __init__(self, x: int, y: int, width: int, height: int, max_length: int = 12):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Maneja eventos de teclado y clic."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < self.max_length:
                if event.unicode.isprintable() and event.unicode not in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                    self.text += event.unicode
    
    def update(self) -> None:
        """Actualiza animación del cursor."""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Dibuja el cuadro de texto."""
        color = INPUT_BOX_ACTIVE_COLOR if self.active else INPUT_BOX_COLOR
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR if self.active else (150, 150, 150), self.rect, 2, border_radius=5)
        
        display_text = self.text if self.text else "Escribe tu nombre..."
        text_color = TEXT_COLOR if self.text else (100, 100, 100)
        text_surf = font.render(display_text, True, text_color)
        
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            cursor_y1 = self.rect.centery - 10
            cursor_y2 = self.rect.centery + 10
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
    
    def get_text(self) -> str:
        """Devuelve el texto ingresado."""
        return self.text.strip()


class HUD:
    """
    Sistema de visualización de información del juego (HUD) y menús.
    Incluye sistema de ingreso de nombre de jugador.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont("Arial", FONT_SIZE_LARGE, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.SysFont("Courier New", FONT_SIZE_SMALL)

        input_width = 300
        input_x = screen_width // 2 - input_width // 2
        self.name_input = InputBox(input_x, 200, input_width, 50, max_length=15)
        
        self.player_name = ""

        button_width, button_height = 200, 50
        center_x = screen_width // 2 - button_width // 2
        self.main_menu_buttons = [
            Button(center_x, 280, button_width, button_height, "Jugar", self._on_play),
            Button(center_x, 350, button_width, button_height, "Ranking", self._on_ranking),
            Button(center_x, 420, button_width, button_height, "Salir", self._on_quit),
        ]
        self.back_button = Button(20, 20, 100, 40, "Atrás", self._on_back)

        self.show_ranking = False
        self.callbacks = {
            "play": None,
            "quit": None,
            "back_to_menu": None,
        }

    def set_callbacks(self, play_callback: Callable, quit_callback: Callable, back_callback: Callable) -> None:
        """Registra callbacks para acciones del menú."""
        self.callbacks["play"] = play_callback
        self.callbacks["quit"] = quit_callback
        self.callbacks["back_to_menu"] = back_callback

    def _on_play(self) -> None:
        """Inicia el juego solo si hay nombre válido."""
        player_name = self.name_input.get_text()
        if player_name:
            self.player_name = player_name
            if self.callbacks["play"]:
                self.callbacks["play"]()
        else:
            self.name_input.active = True

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

    def get_player_name(self) -> str:
        """Devuelve el nombre del jugador actual."""
        return self.player_name if self.player_name else "Jugador"

    def reset_for_new_game(self) -> None:
        """Resetea el input para un nuevo jugador."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Procesa eventos de UI."""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.show_ranking:
            self.back_button.check_hover(mouse_pos)
            self.back_button.handle_event(event)
        else:
            self.name_input.handle_event(event)
            
            player_name = self.name_input.get_text()
            self.main_menu_buttons[0].enabled = bool(player_name)
            
            for button in self.main_menu_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)

    def draw(self, screen: pygame.Surface, game_state: str, game_core=None, score_manager=None) -> None:
        """Renderiza la interfaz según el estado del juego."""
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
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))
        
        label = self.font_small.render("Nombre del Jugador:", True, TEXT_COLOR)
        screen.blit(label, (self.screen_width // 2 - label.get_width() // 2, 170))
        
        self.name_input.update()
        self.name_input.draw(screen, self.font_medium)
        
        if not self.name_input.get_text():
            warning = self.font_small.render("(Ingresa un nombre para jugar)", True, (150, 150, 150))
            screen.blit(warning, (self.screen_width // 2 - warning.get_width() // 2, 260))
        
        for button in self.main_menu_buttons:
            button.draw(screen, self.font_medium)

    def _draw_hud(self, screen: pygame.Surface, game_core) -> None:
        """Dibuja la interfaz durante el juego."""
        name_text = self.font_medium.render(f"Jugador: {self.player_name}", True, HIGHLIGHT_COLOR)
        screen.blit(name_text, (20, 20))
        
        score_text = self.font_medium.render(f"Puntos: {game_core.pacman.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 60))

        level_text = self.font_medium.render(f"Nivel: {game_core.level}", True, TEXT_COLOR)
        screen.blit(level_text, (20, 100))

        lives_text = self.font_medium.render(f"Vidas: {game_core.pacman.lives}", True, TEXT_COLOR)
        screen.blit(lives_text, (20, 140))

        progress = game_core.get_progress_percentage()
        progress_text = self.font_small.render(f"Avance: {progress:.1f}%", True, (100, 255, 100))
        screen.blit(progress_text, (20, 180))

    def _draw_pause(self, screen: pygame.Surface) -> None:
        """Dibuja la pantalla de pausa."""
        title = self.font_large.render("PAUSA", True, TEXT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 150))

        resume = self.font_medium.render("Presiona ESC para reanudar", True, (200, 200, 200))
        screen.blit(resume, (self.screen_width // 2 - resume.get_width() // 2, 300))

    def _draw_game_over(self, screen: pygame.Surface, game_core) -> None:
        """Dibuja la pantalla de fin del juego."""
        title = self.font_large.render("GAME OVER", True, HIGHLIGHT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 120))
        
        player = self.font_medium.render(f"Jugador: {self.player_name}", True, TEXT_COLOR)
        screen.blit(player, (self.screen_width // 2 - player.get_width() // 2, 200))

        score = self.font_medium.render(f"Puntaje Final: {game_core.pacman.score}", True, TEXT_COLOR)
        screen.blit(score, (self.screen_width // 2 - score.get_width() // 2, 250))

        level = self.font_medium.render(f"Nivel Alcanzado: {game_core.level}", True, TEXT_COLOR)
        screen.blit(level, (self.screen_width // 2 - level.get_width() // 2, 300))

        restart = self.font_small.render("Presiona ESPACIO para nuevo jugador", True, (200, 200, 200))
        screen.blit(restart, (self.screen_width // 2 - restart.get_width() // 2, 400))

    def _draw_ranking(self, screen: pygame.Surface, score_manager) -> None:
        """Dibuja la pantalla de ranking - VERSIÓN CORREGIDA."""
        title = self.font_large.render("RANKING", True, TEXT_COLOR)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))

        # ========== FIX: Verificación mejorada ==========
        if not score_manager:
            error = self.font_medium.render("Error al cargar ranking", True, (255, 0, 0))
            screen.blit(error, (self.screen_width // 2 - error.get_width() // 2, 150))
            print("[HUD ERROR] score_manager es None")
            return
        
        # Obtener scores ANTES de verificar si está vacío
        top_scores = score_manager.get_top_scores(10)
        
        # Debug: imprimir cantidad de scores
        print(f"[HUD DEBUG] Scores cargados: {len(top_scores)}")
        
        if len(top_scores) == 0:
            empty = self.font_medium.render("Sin puntajes registrados", True, (150, 150, 150))
            screen.blit(empty, (self.screen_width // 2 - empty.get_width() // 2, 150))
            
            # Sugerencia para el usuario
            hint = self.font_small.render("¡Juega una partida para aparecer aquí!", True, (100, 100, 100))
            screen.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, 200))
            return

        # ========== Renderizar ranking ==========
        y_offset = 150
        for i, entry in enumerate(top_scores, 1):
            # Validar que la entrada tenga todos los campos
            if not isinstance(entry, dict) or 'name' not in entry or 'score' not in entry or 'level' not in entry:
                print(f"[HUD WARNING] Entrada inválida en posición {i}: {entry}")
                continue
            
            # Formatear línea del ranking
            line = f"{i}. {entry['name']:<12} {entry['score']:>6} pts  (Nivel {entry['level']})"
            
            # Color especial para el primer lugar
            color = HIGHLIGHT_COLOR if i == 1 else TEXT_COLOR
            
            # Renderizar texto
            text = self.font_small.render(line, True, color)
            screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, y_offset))
            y_offset += 35
        
        # Mensaje informativo al final
        info = self.font_small.render("Top 10 mejores puntajes", True, (100, 100, 100))
        screen.blit(info, (self.screen_width // 2 - info.get_width() // 2, y_offset + 20))