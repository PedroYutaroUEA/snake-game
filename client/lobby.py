"""Lobby de pré-jogo: seleção e entrada de jogadores para Snake Multiplayer."""

import math
import pygame as pg

from core import config as C
from core.utils import draw_text, draw_panel, draw_overlay
from client.input.manager import InputManager
from client.input import profiles as P

_COUNTDOWN_DURATION = 3.0


class Lobby:
    """Gerencia o estado de entrada de jogadores e a interface de pré-jogo."""

    def __init__(self, input_manager: InputManager):
        self.input_mgr = input_manager
        self.p_colors = getattr(
            C,
            "PLAYER_COLORS",
            {
                1: (255, 255, 255),
                2: (0, 255, 100),
                3: (100, 200, 255),
                4: (255, 200, 0),
            },
        )
        self.lobby_time: float = 0.0
        self._countdown: float = 0.0
        self._starting: bool = False

    def reset(self) -> None:
        """Reseta o estado do lobby para uma nova partida."""
        self.lobby_time = 0.0
        self._countdown = 0.0
        self._starting = False

    def update(self, events: list[pg.event.Event], dt: float = 0.0) -> bool:
        """Processa as conexões e o countdown."""
        self.lobby_time += dt
        self.input_mgr.handle_lobby_logic(events)  # Usando o nome atualizado do manager

        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN and self.input_mgr.get_player_ids():
                    if not self._starting:
                        self._starting = True
                        self._countdown = _COUNTDOWN_DURATION

        if self._starting:
            self._countdown -= dt
            if self._countdown <= 0.0:
                return True

        return False

    def draw(self, screen: pg.Surface, font: pg.font.Font, big_font: pg.font.Font):
        """Renderiza a interface do Lobby utilizando utils otimizados."""
        screen.fill((0, 0, 0))

        label_font = pg.font.SysFont(C.FONT_NAME, 17)
        small_font = pg.font.SysFont(C.FONT_NAME, 15)
        cx = C.WIDTH // 2
        active_ids = self.input_mgr.get_player_ids()

        # ── Títulos ────────────────────────────────────────────────────────────
        draw_text(screen, big_font, "LOBBY", (cx, 30), C.WHITE, center=True)
        draw_text(
            screen,
            label_font,
            "SNAKE MULTIPLAYER",
            (cx, 90),
            (100, 255, 100),
            center=True,
        )

        # ── Slots Dinâmicos ────────────────────────────────────────────────────
        slot_w, slot_h = 178, 148
        total_w = C.MAX_PLAYERS * slot_w + (C.MAX_PLAYERS - 1) * 18
        start_x = cx - total_w // 2
        slot_y = 150

        for i in range(1, C.MAX_PLAYERS + 1):
            sx = start_x + (i - 1) * (slot_w + 18)
            rect = pg.Rect(sx, slot_y, slot_w, slot_h)
            self._draw_slot(screen, font, label_font, small_font, i, rect, active_ids)

        # ── Rodapé e Countdown ─────────────────────────────────────────────────
        self._draw_footer(screen, font, label_font, active_ids)

        if self._starting:
            self._draw_countdown(screen, big_font)

    def _draw_slot(
        self,
        screen: pg.Surface,
        font: pg.font.Font,
        label_font: pg.font.Font,
        small_font: pg.font.Font,
        pid: int,
        rect: pg.Rect,
        active_ids: list[int],
    ) -> None:

        is_active = pid in active_ids
        color = self.p_colors[pid] if is_active else (55, 55, 65)
        r, g, b = color

        # Fundo e Borda (Pulsante se ativo) usando draw_panel do utils
        bg_color = (r, g, b, 18) if is_active else (20, 20, 28, 200)

        if is_active:
            pulse = 0.5 + 0.5 * math.sin(self.lobby_time * 4.0 + pid)
            border_w = 1 + int(pulse * 2)
            border_color = (
                min(255, int(r * 0.7 + 255 * 0.3 * pulse)),
                min(255, int(g * 0.7 + 255 * 0.3 * pulse)),
                min(255, int(b * 0.7 + 255 * 0.3 * pulse)),
            )
        else:
            border_w = 1
            border_color = (55, 55, 65)

        draw_panel(screen, rect, bg_color, border_color, border_w)

        # Barra de Título do Slot
        bar_rect = pg.Rect(rect.x, rect.y, rect.width, 26)
        bar_bg = (r, g, b, 80) if is_active else (40, 40, 50, 200)
        draw_panel(screen, bar_rect, bar_bg, border_color, 0)  # Sem borda interna

        draw_text(
            screen,
            font,
            f"PLAYER  {pid}",
            (rect.centerx, rect.y + 13),
            color,
            center=True,
        )

        # Conteúdo Interno
        if is_active:
            self._draw_active_slot(screen, label_font, small_font, pid, rect, color)
        else:
            self._draw_empty_slot(screen, label_font, small_font, pid, rect)

    def _draw_active_slot(
        self, screen, label_font, small_font, pid, rect, color
    ) -> None:
        device_type = self.input_mgr.get_device_type(pid)

        # Badge
        badge_text = "TECLADO" if device_type == "keyboard" else "CONTROLE"
        badge_color = (220, 220, 100) if device_type == "keyboard" else (100, 220, 220)
        draw_text(
            screen,
            label_font,
            badge_text,
            (rect.centerx, rect.y + 40),
            badge_color,
            center=True,
        )

        # Dicas (Adaptadas para as direções do Snake)
        hy = rect.y + 70
        if device_type == "keyboard":
            hints = P.get_keyboard_hint(f"P{pid}")
            for action, key in hints:
                draw_text(
                    screen,
                    small_font,
                    f"{key} => {action}",
                    (rect.centerx, hy),
                    (180, 180, 180),
                    center=True,
                )
                hy += 18
        else:
            draw_text(
                screen,
                small_font,
                "D-PAD ou Analógico",
                (rect.centerx, hy),
                (180, 180, 180),
                center=True,
            )

        # Status Pronto (Pulsante)
        ready_pulse = 0.7 + 0.3 * math.sin(self.lobby_time * 3.0)
        rc = tuple(min(255, int(c * ready_pulse)) for c in color)
        draw_text(
            screen,
            label_font,
            "PRONTO!",
            (rect.centerx, rect.bottom - 20),
            rc,
            center=True,
        )

    def _draw_empty_slot(self, screen, label_font, small_font, pid, rect) -> None:
        draw_text(
            screen,
            label_font,
            "SLOT VAZIO",
            (rect.centerx, rect.y + 50),
            (70, 70, 80),
            center=True,
        )

        # Tecla de conexão dinamicamente extraída
        p_key = f"P{pid}"
        if p_key in P.KEYBOARD_PROFILES:
            key_name = P.get_key_name(P.KEYBOARD_PROFILES[p_key]["join_key"])
            hints = [f"Pressione '{key_name}'", "para entrar"]
        else:
            hints = ["Conecte controle", "e aperte botão"]

        hy = rect.y + 80
        for hint in hints:
            draw_text(
                screen, small_font, hint, (rect.centerx, hy), (90, 90, 100), center=True
            )
            hy += 16

    def _draw_footer(
        self,
        screen: pg.Surface,
        font: pg.font.Font,
        label_font: pg.font.Font,
        active_ids: list[int],
    ) -> None:
        cx = C.WIDTH // 2
        footer_y = C.HEIGHT - 72

        pg.draw.line(
            screen,
            (50, 50, 60),
            (cx - 280, footer_y - 15),
            (cx + 280, footer_y - 15),
            1,
        )

        if not active_ids:
            msg = 'Pressione "1" (P1) ou "2" (P2) ou botão do controle'
            draw_text(
                screen, label_font, msg, (cx, footer_y), (150, 150, 160), center=True
            )
        elif not self._starting:
            msg = "ENTER para iniciar | outros jogadores ainda podem entrar"
            draw_text(screen, font, msg, (cx, footer_y), (100, 255, 100), center=True)

        draw_text(
            screen,
            label_font,
            "ESC para sair",
            (cx, footer_y + 30),
            (70, 70, 80),
            center=True,
        )

    def _draw_countdown(self, screen: pg.Surface, big_font: pg.font.Font) -> None:
        """Utiliza o draw_overlay do utils para escurecer a tela e plota o contador."""
        draw_overlay(screen, alpha=180)

        cx, cy = C.WIDTH // 2, C.HEIGHT // 2
        secs_left = max(0, math.ceil(self._countdown))

        pulse = 0.7 + 0.3 * math.sin(self.lobby_time * 6.0)
        num_color = (int(255 * pulse), int(255 * pulse), int(100 * pulse))

        draw_text(
            screen, big_font, str(secs_left), (cx, cy - 20), num_color, center=True
        )

        start_font = pg.font.SysFont(C.FONT_NAME, 22)
        draw_text(
            screen,
            start_font,
            "INICIANDO...",
            (cx, cy + 40),
            (200, 200, 200),
            center=True,
        )
