"""Scene state enumeration."""

import enum


class SceneState(enum.Enum):
    """Representa os estados globais da aplicação (FSM).

    - MENU: Tela de título e guia de controles aguardando um pulso de input.
    - LOBBY: Tela de conexão aguardando os jogadores entrarem nos slots.
    - PLAY: Loop principal da gameplay (Física, Renderização e Input em tempo real).
    - GAME_OVER: Tela final de pontuação e transição para recomeçar.
    """

    MENU = enum.auto()
    LOBBY = enum.auto()
    PLAY = enum.auto()
    GAME_OVER = enum.auto()
