import pygame as pg

# --- Traduções amigáveis para as ações do jogo ---
ACTION_LABELS = {
    "up": "Cima",
    "down": "Baixo",
    "right": "Direita",
    "left": "Esquerda",
}

# Teclado para 2 Jogadores na mesma máquina
KEYBOARD_PROFILES = {
    "P1": {
        pg.K_UP: "up",
        pg.K_DOWN: "down",
        pg.K_LEFT: "left",
        pg.K_RIGHT: "right",
        "join_key": pg.K_1,
    },
    "P2": {
        pg.K_w: "up",
        pg.K_s: "down",
        pg.K_a: "left",
        pg.K_d: "right",
        "join_key": pg.K_2,
    },
}

# --- Controle Genérico (D-PAD e Analógico Esquerdo) ---
JOYSTICK_GENERIC = {
    "axes": {
        0: {"neg": "left", "pos": "right"},  # Analógico X
        1: {
            "neg": "up",
            "pos": "down",
        },  # Analógico Y (Atenção à inversão de eixo do Pygame)
    },
    "buttons": {
        # D-PAD (se for lido como botões em alguns controles)
        11: "up",
        12: "down",
        13: "left",
        14: "right",
    },
}


# --- Keybindings helpers functions ---


def get_key_name(key_code: int) -> str:
    """Traduz o código da tecla para uma string legível."""
    name = pg.key.name(key_code)
    # Ajustes cosméticos para teclas comuns
    mapping = {
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→",
    }
    return mapping.get(name, name.capitalize())


def get_keyboard_hint(player_label: str) -> list[tuple[str, str]]:
    """Gera lista de (Ação, Tecla) para o menu/lobby."""
    profile = KEYBOARD_PROFILES.get(player_label, {})
    hints = []

    # Agrupa movimento para economizar espaço
    move_keys = [
        get_key_name(k)
        for k, v in profile.items()
        if v in ["up", "down", "left", "right"]
    ]
    if move_keys:
        hints.append(("Mover", "|".join(move_keys[:3])))

    return hints
