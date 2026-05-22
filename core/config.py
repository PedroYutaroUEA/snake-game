"""Game configuration constants."""

import os

# --- Game Window Settings ---
WIDTH = 960
HEIGHT = 720
FPS = 60

# --- Snake Gameplay Constants ---
GRID_SIZE = 20  # Tamanho em pixels de cada bloco da cobra e da maçã
STARTING_SEGMENTS = 3  # Tamanho inicial da cobra ao nascer
SCORE_PER_FOOD = 10  # Pontos ganhos ao comer
BONUS_SCORE = 50  # Extra score for killing other player

PlayerId = int
LOCAL_PLAYER_ID: PlayerId = 1
MAX_PLAYERS = 4
START_LIVES = 3

# --- Timing & Speed (Tick System) ---
INITIAL_TICK_SPEED = 0.10  # Tempo em segundos entre cada movimento da cobra
TICK_SPEED_DECREMENT = 0.001  # O quanto o tempo diminui (jogo acelera) a cada maçã
MIN_TICK_SPEED = 0.04  # Limite máximo de velocidade para não quebrar a engine
RESPAWN_DELAY = 5.0  # Tempo de espera (em segundos) após uma cobra morrer

# --- Colors ---
PLAYER_COLORS: dict[PlayerId, tuple[int, int, int]] = {
    1: (255, 255, 255),  # Branco (P1)
    2: (0, 255, 100),  # Verde (P2)
    3: (100, 200, 255),  # Ciano (P3)
    4: (255, 200, 0),  # Amarelo (P4)
}
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
FOOD_COLOR = (250, 75, 25)  # Cor avermelhada da maçã
GRID_COLOR = (20, 30, 20)  # Cor sutil para desenhar as linhas de grade (opcional)

# --- Audio mixer settings ---
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512

# --- UI layout ---
FONT_SIZE_SMALL = 22
FONT_SIZE_LARGE = 64
FONT_NAME = "consolas"

RANDOM_SEED = None

# Paths (work from any execution directory).
# config.py lives in core/, so we go one level up to the project root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_PATH = os.path.join(BASE_DIR, "assets", "sounds")
