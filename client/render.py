"""Client-side rendering (pygame) for Snake Multiplayer."""

import math
import pygame as pg

from core import config as C
from core.entities.food import Food
from core.entities.snake import Snake
from core.scene import SceneState
from core.utils import draw_circle, draw_rect, draw_text, draw_overlay, draw_panel
from client.input import profiles as P


class Renderer:
    """Desenha a cena, entidades e a interface sem acoplar regras de negócio."""

    def __init__(
        self,
        screen: pg.Surface,
        config: object = C,
        fonts: dict[str, pg.font.Font] | None = None,
    ) -> None:
        self.screen = screen
        self.config = config
        safe_fonts = fonts or {}
        self.font = safe_fonts["font"]
        self.big = safe_fonts["big"]

        self._draw_dispatch: dict[type, callable] = {
            Snake: self._draw_snake,
            Food: self._draw_food,
        }

    def clear(self) -> None:
        """Limpa a tela e desenha a malha (Grid) de fundo."""
        self.screen.fill(self.config.BLACK)
        self._draw_grid()

    def _draw_grid(self) -> None:
        """Desenha linhas sutis no fundo para representar o tabuleiro."""
        grid_color = getattr(self.config, "GRID_COLOR", (20, 30, 20))
        # Linhas Verticais
        for x in range(0, self.config.WIDTH, self.config.GRID_SIZE):
            pg.draw.line(self.screen, grid_color, (x, 0), (x, self.config.HEIGHT))
        # Linhas Horizontais
        for y in range(0, self.config.HEIGHT, self.config.GRID_SIZE):
            pg.draw.line(self.screen, grid_color, (0, y), (self.config.WIDTH, y))

    def draw_world(self, world: object) -> None:
        """Itera sobre as entidades e delega o desenho."""
        sprites = getattr(world, "all_sprites", [])
        for sprite in sprites:
            drawer = self._draw_dispatch.get(type(sprite))
            if drawer is not None:
                drawer(sprite)

    def draw_hud(
        self,
        scores: dict,
        lives: dict,
        state: SceneState,
        snakes: dict,
    ) -> None:
        """Desenha os painéis informativos no overlay da tela."""
        if state != SceneState.PLAY:
            return

        self._draw_player_panels(scores, lives, snakes)

    def _draw_player_panels(self, scores: dict, lives: dict, snakes: dict) -> None:
        """Renderiza um painel HUD dinâmico para cada jogador."""
        pids = sorted(scores.keys())
        if not pids:
            return

        pw = max(160, self.config.WIDTH // 6)
        ph = 60
        margin = 10

        # Posicionamento nos 4 cantos da tela
        quadrant_positions = [
            (margin, margin),
            (self.config.WIDTH - pw - margin, margin),
            (margin, self.config.HEIGHT - ph - margin),
            (self.config.WIDTH - pw - margin, self.config.HEIGHT - ph - margin),
        ]

        for idx, pid in enumerate(pids):
            qpos = quadrant_positions[idx % 4]
            snake = snakes.get(pid)
            self._draw_single_player_panel(
                pid, qpos, pw, ph, scores[pid], lives[pid], snake
            )

    def _draw_single_player_panel(
        self,
        pid: int,
        pos: tuple,
        pw: int,
        ph: int,
        score: int,
        life_count: int,
        snake: Snake | None,
    ) -> None:
        x, y = pos
        color = self.config.PLAYER_COLORS.get(pid, self.config.WHITE)
        eliminated = life_count <= 0

        # --- Fundo e Borda usando draw_panel ---
        border_color = (80, 80, 80) if eliminated else color
        rect = pg.Rect(x, y, pw, ph)
        draw_panel(self.screen, rect, (0, 0, 0, 160), border_color, 1)

        # --- Barra de Título ---
        bar_rect = pg.Rect(x, y, pw, 20)
        r, g, b = color
        bar_bg = (r, g, b, 60) if eliminated else (r, g, b, 110)
        draw_panel(self.screen, bar_rect, bar_bg, border_color, 0)

        draw_text(self.screen, self.font, f"PLAYER {pid}", (x + 8, y + 1), color)

        # --- Textos ---
        if eliminated:
            draw_text(
                self.screen,
                self.font,
                "ELIMINATED",
                (x + pw // 2, y + 30),
                (200, 60, 60),
                center=True,
            )
        else:
            draw_text(
                self.screen,
                self.font,
                f"{score:07d}",
                (x + 8, y + 24),
                self.config.WHITE,
            )
            self._draw_life_icons(x + 8, y + 44, life_count, color)

    def _draw_life_icons(self, x: int, y: int, count: int, color: tuple) -> None:
        """Desenha as vidas como pequenos quadrados (lembrando blocos da cobra)."""
        icon_size, gap = 10, 4
        for i in range(count):
            ix = x + i * (icon_size + gap)
            pg.draw.rect(self.screen, color, (ix, y, icon_size, icon_size), 2)

    def _draw_snake(self, snake: Snake) -> None:
        if not snake.alive:
            return

        base_color = self.config.PLAYER_COLORS.get(snake.player_id, self.config.WHITE)

        # A cabeça é levemente mais brilhante e saturada
        head_color = (
            min(255, base_color[0] + 50),
            min(255, base_color[1] + 50),
            min(255, base_color[2] + 50),
        )

        for i, seg_pos in enumerate(snake.segments):
            color = head_color if i == 0 else base_color
            draw_rect(self.screen, seg_pos, self.config.GRID_SIZE, color)

            # Olhinhos na cabeça para dar charme e indicar a direção
            if i == 0:
                eye_color = (0, 0, 0)
                cx, cy = seg_pos.x, seg_pos.y
                gs = self.config.GRID_SIZE

                # Posicionamento dos olhos baseado na direção atual
                if snake.direction.y < 0:  # Cima
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + 4), int(cy + 4)), 2
                    )
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + gs - 4), int(cy + 4)), 2
                    )
                elif snake.direction.y > 0:  # Baixo
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + 4), int(cy + gs - 4)), 2
                    )
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + gs - 4), int(cy + gs - 4)), 2
                    )
                elif snake.direction.x < 0:  # Esquerda
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + 4), int(cy + 4)), 2
                    )
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + 4), int(cy + gs - 4)), 2
                    )
                elif snake.direction.x > 0:  # Direita
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + gs - 4), int(cy + 4)), 2
                    )
                    pg.draw.circle(
                        self.screen, eye_color, (int(cx + gs - 4), int(cy + gs - 4)), 2
                    )

    def _draw_food(self, food: Food) -> None:
        """A comida (maçã) é desenhada como um círculo."""
        food_color = getattr(self.config, "FOOD_COLOR", (250, 75, 25))
        draw_circle(self.screen, food.pos, self.config.GRID_SIZE, food_color)

        # Desenha um pequeno "cabinho" verde no topo da maçã
        stem_x = food.pos.x + self.config.GRID_SIZE // 2
        stem_y = food.pos.y + self.config.GRID_SIZE // 4
        pg.draw.line(
            self.screen, (50, 200, 50), (stem_x, stem_y), (stem_x + 3, stem_y - 4), 2
        )

    def draw_menu(self, menu_time: float = 0.0) -> None:
        """Tela inicial estilizada com guia dinâmico de controles."""
        self.clear()  # Garante que o grid de fundo apareça no menu
        cx = self.config.WIDTH // 2

        # --- Título Pulsante ---
        pulse = 0.85 + 0.15 * math.sin(menu_time * 2.2)
        title_color = (int(200 * pulse), int(255 * pulse), int(200 * pulse))

        # Glow text
        for glow_scale, alpha in ((1.1, 30), (1.05, 60)):
            glow_size = int(self.config.FONT_SIZE_LARGE * glow_scale)
            glow_font = pg.font.SysFont(self.config.FONT_NAME, glow_size, bold=True)
            glow_surf = glow_font.render("SNAKE MULTIPLAYER", True, (50, 255, 100))
            glow_surf.set_alpha(alpha)
            self.screen.blit(
                glow_surf,
                (cx - glow_surf.get_width() // 2, self.config.HEIGHT // 4 - 10),
            )

        # Main Text
        title_surf = self.big.render("SNAKE MULTIPLAYER", True, title_color)
        ty = self.config.HEIGHT // 4
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, ty))

        # --- Subtítulo ---
        div_y = ty + title_surf.get_height() + 20
        pg.draw.line(self.screen, (60, 80, 60), (cx - 220, div_y), (cx + 220, div_y), 1)

        # --- Guia de Controles (Extraído dinamicamente do profiles.py) ---
        guide_y = div_y + 20
        label_font = pg.font.SysFont(self.config.FONT_NAME, 17)

        sections = []
        for p_label, color in [("P1", (255, 255, 255)), ("P2", (0, 255, 100))]:
            hints = P.get_keyboard_hint(p_label)
            join_k = P.get_key_name(P.KEYBOARD_PROFILES[p_label]["join_key"])
            hints.append(("Entrar", f'Tecla "{join_k}"'))
            sections.append((f"TECLADO {p_label}", color, hints))

        joy_hints = [("Mover", "D-PAD / Analógico"), ("Entrar", "Botão A / X")]
        sections.append(("CONTROLE", (100, 200, 255), joy_hints))

        col_w = self.config.WIDTH // 3
        for col_idx, (header, hcolor, rows) in enumerate(sections):
            col_x = col_idx * col_w + col_w // 2
            draw_text(
                self.screen, label_font, header, (col_x, guide_y), hcolor, center=True
            )
            pg.draw.line(
                self.screen,
                hcolor,
                (col_x - 70, guide_y + 15),
                (col_x + 70, guide_y + 15),
                1,
            )

            row_y = guide_y + 30
            for action, key in rows:
                draw_text(
                    self.screen,
                    label_font,
                    f"{action}:",
                    (col_x - 70, row_y),
                    (140, 140, 140),
                )
                draw_text(
                    self.screen,
                    label_font,
                    key,
                    (col_x - 70 + 60, row_y),
                    (210, 210, 210),
                )
                row_y += 22

        # --- Rodapé ---
        footer_y = self.config.HEIGHT - 54
        pg.draw.line(
            self.screen,
            (60, 80, 60),
            (cx - 220, footer_y - 8),
            (cx + 220, footer_y - 8),
            1,
        )

        if int(menu_time * 2) % 2 == 0:
            draw_text(
                self.screen,
                self.font,
                "Pressione uma tecla para comecar",
                (cx, footer_y),
                center=True,
            )

        draw_text(
            self.screen,
            label_font,
            "ESC para sair",
            (cx, footer_y + 26),
            (90, 90, 90),
            center=True,
        )

    def draw_game_over(self, scores: dict, elapsed: float = 0.0) -> None:
        """Tela de fim de jogo e placar."""
        cx = self.config.WIDTH // 2

        # Efeito de escurecer a tela progressivamente
        fade_alpha = min(200, int(elapsed * 340))
        draw_overlay(self.screen, alpha=fade_alpha)

        content_alpha = max(0, min(255, int((elapsed - 0.35) * 510)))
        if content_alpha == 0:
            return

        medium_font = pg.font.SysFont(self.config.FONT_NAME, 22)

        # --- Título ---
        draw_text(
            self.screen, self.big, "GAME OVER", (cx, 80), (255, 80, 80), center=True
        )

        # --- Ranking ---
        draw_text(
            self.screen,
            medium_font,
            "RANKING FINAL DE MAÇÃS",
            (cx, 180),
            (180, 200, 180),
            center=True,
        )

        sorted_pids = sorted(scores.keys(), key=lambda p: scores[p], reverse=True)
        row_h = 38
        row_w = 400

        for rank, pid in enumerate(sorted_pids, start=1):
            ry = 220 + (rank - 1) * (row_h + 6)
            player_color = self.config.PLAYER_COLORS.get(pid, self.config.WHITE)

            # --- Uso do draw_panel para as linhas de ranking ---
            row_rect = pg.Rect(cx - row_w // 2, ry, row_w, row_h)
            bg_color = (255, 255, 255, 15) if rank == 1 else (0, 0, 0, 80)
            draw_panel(self.screen, row_rect, bg_color, player_color, 1)

            draw_text(
                self.screen,
                medium_font,
                f"#{rank} PLAYER {pid}",
                (row_rect.x + 15, ry + 10),
                player_color,
            )

            apples = scores[pid] // getattr(self.config, "SCORE_PER_FOOD", 10)
            length = getattr(self.config, "STARTING_SEGMENTS", 3) + apples

            draw_text(
                self.screen,
                medium_font,
                f"Tam: {length}",
                (row_rect.x + 200, ry + 10),
                (200, 200, 200),
            )
            draw_text(
                self.screen,
                medium_font,
                f"{scores[pid]:05d} PTS",
                (row_rect.x + 300, ry + 10),
                (255, 215, 60),
            )

        # --- Footer ---
        if elapsed > 1.2 and int(elapsed * 2) % 2 == 0:
            draw_text(
                self.screen,
                self.font,
                "Pressione ENTER para jogar novamente",
                (cx, self.config.HEIGHT - 80),
                (200, 200, 200),
                center=True,
            )
