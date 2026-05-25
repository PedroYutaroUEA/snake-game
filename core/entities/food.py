"""Food entity."""

from core import config as C
from core.entities import Entity
from core.utils import Vec


class Food(Entity):
    """Representa a maçã consumível no grid."""

    def __init__(self, pos: Vec) -> None:
        self.r = C.GRID_SIZE // 2
        self.pos = Vec(pos)
        super().__init__()

        # O _sync_rect() centralizará a bounding box na coordenada correta
        self._sync_rect()

    def update(self, dt: float) -> None:
        """Cumpre o contrato da Entity. A comida é estática."""
        pass
