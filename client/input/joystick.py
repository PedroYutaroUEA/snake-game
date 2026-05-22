"""Dispositivo de entrada genérico para Joysticks e Gamepads."""

import pygame as pg
from client.input.device import InputDevice
from core.commands import PlayerCommand


class JoystickDevice(InputDevice):
    """Lê entradas de controles como Playstation/Xbox, suportando Analógico e D-PAD."""

    def __init__(self, joystick: pg.joystick.Joystick, profile: dict):
        super().__init__()
        self.joy = joystick
        self.profile = profile
        self.deadzone = 0.4

    def handle_event(self, event: pg.event.Event) -> None:
        # Os comandos de direção serão lidos continuamente (Polling) no build_command.
        pass

    def build_command(self) -> PlayerCommand:
        cmd_dict = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        # 1. Processa Analógicos (Eixos)
        for axis_id, mapping in self.profile.get("axes", {}).items():
            if axis_id < self.joy.get_numaxes():
                val = self.joy.get_axis(axis_id)
                if val < -self.deadzone and "neg" in mapping:
                    cmd_dict[mapping["neg"]] = True
                if val > self.deadzone and "pos" in mapping:
                    cmd_dict[mapping["pos"]] = True

        # 2. Processa D-PAD (Hats)
        # Pygame retorna o hat como uma tupla (x, y) de valores -1, 0 ou 1.
        if 0 in self.profile.get("hats", {}) and self.joy.get_numhats() > 0:
            hat_x, hat_y = self.joy.get_hat(0)

            if hat_x == -1:
                cmd_dict["left"] = True
            elif hat_x == 1:
                cmd_dict["right"] = True

            # No Pygame, Y=1 costuma ser cima, mas depende do driver do SO.
            # A checagem abaixo lida com o mapeamento padrão SDL2.
            if hat_y == 1:
                cmd_dict["up"] = True
            elif hat_y == -1:
                cmd_dict["down"] = True

        return PlayerCommand(**cmd_dict)
