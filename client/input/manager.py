"""Gerenciador central de dispositivos de entrada para o Snake Multiplayer."""

import pygame as pg

from core import config as C
from core.commands import PlayerCommand
from client.input.device import InputDevice
from client.input.joystick import JoystickDevice
from client.input.keyboard import KeyboardDevice
from client.input.profiles import (
    JOYSTICK_GENERIC,
    JOYSTICK_PLAYSTATION,
    JOYSTICK_XBOX,
    KEYBOARD_PROFILES,
)


class InputManager:
    """Gerencia múltiplos hardwares conectados e os mapeia para os IDs lógicos dos jogadores."""

    def __init__(self) -> None:
        self.devices: dict[C.PlayerId, InputDevice] = {}
        self.active_joystick_ids = set()
        self.joysticks = []

        # Inicializa o subsistema de joystick do Pygame
        pg.joystick.init()
        for i in range(pg.joystick.get_count()):
            joy = pg.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)
            print(f"[INPUT] Joystick Detectado: {joy.get_name()}")

    def _get_next_available_joystick_id(self) -> int | None:
        """Encontra o menor ID disponível (priorizando 3 e 4 para não roubar a vaga do teclado)."""
        # Tenta primeiro os slots 3 e 4 (tradicionalmente de controles)
        for i in range(3, C.MAX_PLAYERS + 1):
            if i not in self.devices:
                return i

        # Se os slots 3 e 4 estiverem cheios, tenta os slots 1 e 2
        for i in range(1, 3):
            if i not in self.devices:
                return i

        return None

    def handle_lobby_logic(self, events: list[pg.event.Event]) -> None:
        """Processa as entradas no lobby (conexão/desconexão de jogadores)."""
        for event in events:
            # --- Entrada por Teclado ---
            if event.type == pg.KEYDOWN:
                for profile_name, mapping in KEYBOARD_PROFILES.items():
                    if event.key == mapping["join_key"]:
                        # Ex: "P1" vira 1, "P2" vira 2
                        pid = int(profile_name[-1])

                        # Alterna a conexão do jogador (Toggle on/off)
                        if pid not in self.devices:
                            print(f"[LOBBY] Teclado conectado no Slot {pid}")
                            self.devices[pid] = KeyboardDevice(mapping)
                        else:
                            print(f"[LOBBY] Teclado desconectado do Slot {pid}")
                            self.devices.pop(pid)

            # --- Entrada por Joystick ---
            elif event.type == pg.JOYBUTTONDOWN:
                if event.joy not in self.active_joystick_ids:
                    pid = self._get_next_available_joystick_id()
                    if pid:
                        joy = pg.joystick.Joystick(event.joy)
                        self.assign_joystick_profile(pid, joy)
                        self.active_joystick_ids.add(event.joy)
                    else:
                        print("[LOBBY] Limite máximo de jogadores atingido!")

    def assign_joystick_profile(
        self, player_id: int, joystick: pg.joystick.Joystick
    ) -> None:
        """Identifica a assinatura (nome) do dispositivo USB/Bluetooth e injeta o mapeamento correto."""
        name = joystick.get_name().lower()

        if "xbox" in name or "x-input" in name:
            profile = JOYSTICK_XBOX
            profile_name = "Xbox"
        elif any(
            ps_name in name
            for ps_name in [
                "ps4",
                "ps5",
                "dualshock",
                "dualsense",
                "wireless controller",
            ]
        ):
            profile = JOYSTICK_PLAYSTATION
            profile_name = "PlayStation"
        else:
            profile = JOYSTICK_GENERIC
            profile_name = "Genérico"

        print(
            f"[LOBBY] Joystick '{name}' associado ao Player {player_id} usando perfil {profile_name}."
        )
        self.devices[player_id] = JoystickDevice(joystick, profile)

    def handle_gameplay_events(self, events: list[pg.event.Event]) -> None:
        """Roteia eventos pontuais para cada dispositivo.

        Nota: No Snake, o movimento é feito majoritariamente por polling (leitura contínua).
        Mas mantemos a chamada por questões arquiteturais (ex: botão de pause futuro).
        """
        for event in events:
            for device in self.devices.values():
                device.handle_event(event)

    def get_player_ids(self) -> list[C.PlayerId]:
        """Retorna uma lista ordenada com os IDs dos jogadores ativos no Lobby."""
        return sorted(list(self.devices.keys()))

    def get_all_commands(self) -> dict[C.PlayerId, PlayerCommand]:
        """Gera o dicionário de comandos empacotados para ser consumido pelo World Engine."""
        return {pid: dev.build_command() for pid, dev in self.devices.items()}

    def get_device_type(self, pid: C.PlayerId) -> str:
        """Fornece metadados para a UI renderizar o ícone de 'Teclado' ou 'Controle'."""
        device = self.devices.get(pid)
        if device is None:
            return ""
        return "joystick" if isinstance(device, JoystickDevice) else "keyboard"
