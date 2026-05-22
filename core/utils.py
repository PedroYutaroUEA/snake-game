"""Common game utilities for Snake Multiplayer."""

import random
from typing import Tuple

import pygame as pg

from core import config as C

Vec = pg.math.Vector2


# --- Matemática e Lógica de Grid ---


def wrap_pos(pos: Vec) -> Vec:
    """Faz a cobra reaparecer no lado oposto ao cruzar a borda."""
    return Vec(pos.x % C.WIDTH, pos.y % C.HEIGHT)


def rand_grid_pos() -> Vec:
    """Gera uma coordenada aleatória estritamente alinhada ao Grid."""
    cols = C.WIDTH // C.GRID_SIZE
    rows = C.HEIGHT // C.GRID_SIZE

    # Sorteia uma coluna e linha, e multiplica pelo tamanho do grid
    x = random.randrange(0, cols) * C.GRID_SIZE
    y = random.randrange(0, rows) * C.GRID_SIZE

    return Vec(x, y)


def is_out_of_bounds(pos: Vec) -> bool:
    """Verifica se a posição colidiu com a parede do mapa."""
    return pos.x < 0 or pos.x >= C.WIDTH or pos.y < 0 or pos.y >= C.HEIGHT


# --- Desenho Otimizado ---


def draw_rect(
    surface: pg.Surface, pos: Vec, size: int, color: Tuple[int, int, int]
) -> None:
    """Desenha um bloco alinhado ao grid (usado para segmentos da cobra)."""
    rect = pg.Rect(int(pos.x), int(pos.y), size, size)
    pg.draw.rect(surface, color, rect)

    # Opcional: Desenha uma borda levemente mais escura para destacar os segmentos
    border_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
    pg.draw.rect(surface, border_color, rect, 1)


def draw_circle(
    surface: pg.Surface, pos: Vec, size: int, color: Tuple[int, int, int]
) -> None:
    """Desenha um círculo alinhado ao grid (usado para a maçã)."""
    # O + size // 2 é para compensar o fato do Pygame desenhar o círculo a partir do centro,
    # enquanto nosso Vec aponta para o topo esquerdo da célula do grid.
    center = (int(pos.x + size // 2), int(pos.y + size // 2))
    radius = size // 2
    pg.draw.circle(surface, color, center, radius)


def draw_text(
    surface: pg.Surface,
    font: pg.font.Font,
    text: str,
    pos: Tuple[int, int],
    color: Tuple[int, int, int] = C.WHITE,
    center: bool = False,
) -> None:
    """Renderiza texto com opção de centralização automática."""
    label = font.render(text, True, color)
    rect = label.get_rect(center=pos) if center else label.get_rect(topleft=pos)
    surface.blit(label, rect)
