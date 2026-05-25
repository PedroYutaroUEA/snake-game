"""Game audio (client-side).

- World does not play sounds (low coupling).
- World generates events (strings) and Game decides what to play.
"""

from dataclasses import dataclass

import pygame as pg
from core import config as C


@dataclass(slots=True)
class SoundPack:
    """SFX Pack for snake game"""

    hit_boundary: pg.mixer.Sound
    hit_player: pg.mixer.Sound
    eat_1: pg.mixer.Sound
    eat_2: pg.mixer.Sound


def load_sounds(base_path: str) -> SoundPack:
    """Loads SoundBack for a given SFX path"""

    def s(name: str) -> pg.mixer.Sound:
        return pg.mixer.Sound(f"{base_path}/{name}")

    return SoundPack(
        hit_boundary=s(C.HIT_BOUNDARY),
        hit_player=s(C.HIT_PLAYER),
        eat_1=s(C.EAT_1),
        eat_2=s(C.EAT_2),
    )
