"""Collision detection and resolution for Snake Multiplayer."""

from dataclasses import dataclass, field
from typing import Dict, List

from core import config as C
from core.entities import Food, Snake
from core.utils import is_out_of_bounds

import pygame as pg


@dataclass
class CollisionResult:
    """Resultado do processamento de colisões de um único frame (tick)."""

    events: list[str] = field(default_factory=list)
    score_deltas: dict[C.PlayerId, int] = field(default_factory=dict)

    # Usamos Set (conjunto) para mortes, evitando duplicatas se a cobra
    # bater no próprio corpo e na parede ao mesmo tempo.
    snake_deaths: set[C.PlayerId] = field(default_factory=set)
    snakes_to_grow: list[C.PlayerId] = field(default_factory=list)
    food_eaten: list[Food] = field(default_factory=list)


class CollisionManager:
    """Árbitro central de regras espaciais na malha (Grid)."""

    def resolve(
        self, snakes: Dict[C.PlayerId, Snake], foods: pg.sprite.Group | List[Food]
    ) -> CollisionResult:
        result = CollisionResult()

        self._head_vs_boundary(snakes, result)
        self._head_vs_body(snakes, result)
        self._head_vs_food(snakes, foods, result)

        return result

    def _head_vs_boundary(
        self, snakes: Dict[C.PlayerId, Snake], result: CollisionResult
    ) -> None:
        """Verifica se alguma cabeça saiu dos limites da janela."""
        for snake in snakes.values():
            if not snake.alive:
                continue

            # A cabeça é sempre o índice 0
            head_pos = snake.segments[0]
            if is_out_of_bounds(head_pos):
                result.snake_deaths.add(snake.player_id)
                result.events.append("snake_hit_wall")

    def _head_vs_body(
        self, snakes: Dict[C.PlayerId, Snake], result: CollisionResult
    ) -> None:
        """Verifica se a cabeça da cobra atingiu qualquer segmento (dela mesma ou de oponentes)."""
        for snake in snakes.values():
            if not snake.alive:
                continue
            if getattr(snake, "invuln_timer", 0) > 0:
                continue

            head_pos = snake.segments[0]

            for other_snake in snakes.values():
                if not other_snake.alive:
                    continue
                if getattr(other_snake, "invuln_timer", 0) > 0:
                    continue

                # Se estivermos checando a cobra contra ela mesma, pulamos o índice 0 (cabeça)
                # Se for contra outro jogador, a cabeça do outro também é um obstáculo fatal (head-to-head)
                start_idx = 1 if snake.player_id == other_snake.player_id else 0

                for i in range(start_idx, len(other_snake.segments)):
                    if head_pos == other_snake.segments[i]:
                        result.snake_deaths.add(snake.player_id)

                        # Lógica de PVP: Se bateu no inimigo, o inimigo ganha pontos pelo "abate"
                        if snake.player_id != other_snake.player_id:
                            result.score_deltas[other_snake.player_id] = (
                                result.score_deltas.get(other_snake.player_id, 0)
                                + C.BONUS_SCORE
                            )
                            result.events.append("snake_pvp_kill")
                        else:
                            result.events.append("snake_hit_self")

                        # Já morreu, não precisa checar o resto do corpo deste oponente
                        break

    def _head_vs_food(
        self,
        snakes: Dict[C.PlayerId, Snake],
        foods: list[Food],
        result: CollisionResult,
    ) -> None:
        """Processa a coleta da maçã no mapa."""
        for snake in snakes.values():
            if not snake.alive:
                continue

            # Não permite comer se a cobra bateu e morreu no mesmo frame
            if snake.player_id in result.snake_deaths:
                continue

            head_pos = snake.segments[0]

            for food in foods:
                if food in result.food_eaten:
                    continue  # Outra cobra já processou esta maçã no mesmo frame

                if head_pos == food.pos:
                    result.food_eaten.append(food)
                    result.snakes_to_grow.append(snake.player_id)
                    # Adiciona a pontuação base configurada
                    result.score_deltas[snake.player_id] = result.score_deltas.get(
                        snake.player_id, 0
                    ) + getattr(C, "SCORE_PER_FOOD", 10)
                    result.events.append(f"food_eaten_{snake.player_id}")
