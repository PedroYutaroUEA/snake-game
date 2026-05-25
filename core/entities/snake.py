"""Snake entity."""

from core.commands import PlayerCommand
from core.utils import Vec
from core.entities import Entity
import core.config as C


class Snake(Entity):
    """Representa um jogador (Cobra) composto por múltiplos segmentos."""

    def __init__(self, player_id: C.PlayerId, start_pos: Vec, start_dir: Vec) -> None:
        self.r = C.GRID_SIZE // 2
        self.pos = Vec(start_pos)
        super().__init__()

        self.player_id = player_id
        self.alive = True
        self.invuln_timer = 2.0  # 2 Segundos de Invencibilidade ao nascer

        # O corpo nasce "para trás" baseado no vetor de direção
        self.segments: list[Vec] = [
            Vec(start_pos.x - (i * start_dir.x), start_pos.y - (i * start_dir.y))
            for i in range(C.STARTING_SEGMENTS)
        ]

        self.direction = Vec(start_dir)
        self.next_direction = self.direction

    def apply_command(self, cmd: PlayerCommand):
        """Atualiza a intenção de movimento, bloqueando a 'ré'."""
        if cmd.up and self.direction.y == 0:
            self.next_direction = Vec(0, -C.GRID_SIZE)
        elif cmd.down and self.direction.y == 0:
            self.next_direction = Vec(0, C.GRID_SIZE)
        elif cmd.left and self.direction.x == 0:
            self.next_direction = Vec(-C.GRID_SIZE, 0)
        elif cmd.right and self.direction.x == 0:
            self.next_direction = Vec(C.GRID_SIZE, 0)

    def step(self):
        """Movimenta a cobra logicamente na grade. Chamado pelo World a cada tick."""
        if not self.alive:
            return

        self.direction = self.next_direction

        # O corpo segue a cabeça (copia a posição do segmento anterior)
        for i in range(len(self.segments) - 1, 0, -1):
            self.segments[i] = Vec(self.segments[i - 1])

        # Move a cabeça
        self.segments[0] += self.direction

        # Sincroniza o pos central da entidade com a cabeça para o `_sync_rect` do base.py
        self.pos = Vec(self.segments[0])
        self._sync_rect()

    def update(self, dt: float) -> None:
        """Cumpre o contrato da Entity e decresce a invencibilidade a 60FPS."""
        if getattr(self, "invuln_timer", 0) > 0:
            self.invuln_timer -= dt

    def grow(self) -> None:
        """Adiciona um novo segmento na posição da cauda atual."""
        self.segments.append(Vec(self.segments[-1]))
