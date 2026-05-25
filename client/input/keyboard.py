"""Dispositivo de entrada para Teclados físicos."""

import pygame as pg
from client.input.device import InputDevice
from core.commands import PlayerCommand


class KeyboardDevice(InputDevice):
    """Mapeia teclas físicas para nomes de atributos booleanos em PlayerCommand."""

    def __init__(self, key_map: dict[int, str]):
        super().__init__()
        self.key_map = key_map

    def handle_event(self, event: pg.event.Event) -> None:
        """A cobra só usa polling direcional, eventos discretos são ignorados."""
        pass

    def build_command(self) -> PlayerCommand:
        pressed = pg.key.get_pressed()
        cmd_data = {"up": False, "down": False, "left": False, "right": False}

        for key_code, action in self.key_map.items():
            if isinstance(key_code, int) and action in cmd_data:
                if pressed[key_code]:
                    cmd_data[action] = True

        return PlayerCommand(**cmd_data)
