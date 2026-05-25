from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerCommand:
    """Comandos aplicados a uma cobra em um frame."""

    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
