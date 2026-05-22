"""World state and logic orchestration for Snake Multiplayer."""

from typing import Dict, List
import pygame as pg

from core import config as C
from core.collisions import CollisionManager
from core.commands import PlayerCommand
from core.entities.food import Food
from core.entities.snake import Snake
from core.utils import Vec, rand_grid_pos


class World:
    """Orquestrador do estado da partida, entidades e sistema de Ticks."""

    def __init__(self, player_ids: List[C.PlayerId]) -> None:
        self.active_player_ids = player_ids
        self.game_over = False
        self.tick_speed = None
        self._init_state()

    def _init_state(self) -> None:
        """Inicializa (ou reinicia) todo o estado mutável da simulação."""
        # Assume 1 vidas padrão por jogador. Pode ser movido para config no futuro.
        self.scores: Dict[C.PlayerId, int] = {pid: 0 for pid in self.active_player_ids}
        self.lives: Dict[C.PlayerId, int] = {
            pid: C.START_LIVES for pid in self.active_player_ids
        }
        self.respawn_timers: Dict[C.PlayerId, float] = {}

        self.snakes: Dict[C.PlayerId, Snake] = {}
        self.foods = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        # Sistema de Ticks
        self.tick_timer = 0.0
        self.events: list[str] = []
        self.tick_speed = float(C.INITIAL_TICK_SPEED)

        self._collision_mgr = CollisionManager()
        self.game_over = False

        # Prepara o mapa
        for pid in self.active_player_ids:
            self.spawn_player(pid)

        # Spawna a primeira maçã
        self.spawn_food()

    def reset(self) -> None:
        """Reinicia o mundo in-place, mantendo os mesmos jogadores do lobby."""
        self._init_state()

    def spawn_player(self, player_id: C.PlayerId) -> None:
        """Spawna uma cobra em sua posição inicial baseada no ID."""
        start_pos = self._get_start_pos(player_id)
        snake = Snake(player_id, start_pos)
        self.snakes[player_id] = snake
        self.all_sprites.add(snake)

    def _get_start_pos(self, pid: C.PlayerId) -> Vec:
        """Define posições fixas nos quadrantes para evitar colisões no nascimento."""
        offset = C.GRID_SIZE * 5
        offsets = {
            1: (offset, offset),  # Top-Left
            2: (C.WIDTH - offset, C.HEIGHT - offset),  # Bottom-Right
            3: (C.WIDTH - offset, offset),  # Top-Right
            4: (offset, C.HEIGHT - offset),  # Bottom-Left
        }
        ox, oy = offsets.get(pid, (C.WIDTH // 2, C.HEIGHT // 2))

        # Garante que a posição inicial esteja perfeitamente alinhada à malha
        ox = (ox // C.GRID_SIZE) * C.GRID_SIZE
        oy = (oy // C.GRID_SIZE) * C.GRID_SIZE

        return Vec(ox, oy)

    def spawn_food(self) -> None:
        """Spawna uma maçã garantindo que não caia dentro do corpo de uma cobra."""
        while True:
            pos = rand_grid_pos()
            collision = False

            for snake in self.snakes.values():
                if not snake.alive:
                    continue
                # Verifica se a maçã sorteada caiu exatamente em cima de um segmento
                if any(pos == seg for seg in snake.segments):
                    collision = True
                    break

            if not collision:
                food = Food(pos)
                self.foods.add(food)
                self.all_sprites.add(food)
                break

    def update(self, dt: float, commands: Dict[C.PlayerId, PlayerCommand]) -> None:
        """Atualiza a lógica principal a cada frame."""
        if self.game_over:
            return
        self.events.clear()

        # 1. Aplica comandos (Capturados a 60FPS para garantir fluidez no Input)
        self._apply_players_commands(commands)

        # 2. Resolve penalidades de tempo (Delay de morte)
        self._update_timers(dt)

        # 3. Avança a física e colisões apenas quando o tick estourar
        self.tick_timer += dt

        # O uso de while garante que se houver uma travada de CPU, o jogo pulará
        # fisicamente a quantidade de ticks necessários (catch-up)
        while self.tick_timer >= self.tick_speed:
            self.tick_timer -= self.tick_speed
            self._step_snakes()
            self._handle_collisions()

    def _apply_players_commands(
        self, commands: Dict[C.PlayerId, PlayerCommand]
    ) -> None:
        """Repassa a intenção de movimento para as entidades vivas."""
        for pid, cmd in commands.items():
            snake = self.snakes.get(pid)
            if snake and snake.alive:
                snake.apply_command(cmd)

    def _update_timers(self, dt: float) -> None:
        """Gerencia os cooldowns de respawn dos jogadores."""
        for pid in list(self.respawn_timers.keys()):
            self.respawn_timers[pid] -= dt
            if self.respawn_timers[pid] <= 0:
                del self.respawn_timers[pid]
                self.spawn_player(pid)

    def _step_snakes(self) -> None:
        """Informa a todas as cobras vivas para darem um passo lógico na grade."""
        for snake in self.snakes.values():
            if snake.alive:
                snake.step()

    def _handle_collisions(self) -> None:
        """Consulta o árbitro de colisões e aplica as consequências no World."""
        result = self._collision_mgr.resolve(self.snakes, self.foods)
        self.events.extend(result.events)

        # 1. Aplica pontuações (inclui bônus de abates de PVP)
        for player_id, delta in result.score_deltas.items():
            if player_id in self.scores:
                self.scores[player_id] += delta

        # 2. Processa maçãs consumidas
        for food in result.food_eaten:
            food.kill()
            self.spawn_food()

            # Dinâmica: O jogo fica mais rápido a cada maçã consumida
            self.tick_speed = max(
                C.MIN_TICK_SPEED, self.tick_speed - C.TICK_SPEED_DECREMENT
            )

        # 3. Adiciona segmentos nas cobras que comeram
        for pid in result.snakes_to_grow:
            if pid in self.snakes:
                self.snakes[pid].grow()

        # 4. Abate os jogadores que colidiram
        for player_id in result.snake_deaths:
            self._snake_die(player_id)

    def _snake_die(self, pid: C.PlayerId) -> None:
        """Inicia a sequência de destruição e possível renascimento."""
        snake = self.snakes.get(pid)
        if not snake or not snake.alive:
            return

        snake.alive = False
        snake.kill()  # Remove do grupo de renderização
        self.lives[pid] -= 1

        if self.lives[pid] > 0:
            # Jogador perdeu o corpo, mas entra em modo de espera
            self.respawn_timers[pid] = float(getattr(C, "RESPAWN_DELAY", 5.0))

        # O jogo encerra quando nenhuma cobra viva ou esperando respawn existir
        if all(life <= 0 for life in self.lives.values()):
            self.game_over = True
