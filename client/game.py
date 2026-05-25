"""Game loop and scenes (menu, lobby, play, game over) for Snake Multiplayer."""

import sys
import pygame as pg

from client.input.manager import InputManager
from client.lobby import Lobby
from core import config as C
from core.scene import SceneState
from client.audio.pack import load_sounds
from client.audio.manager import AudioManager
from client.renderer import Renderer
from core.world import World


class Game:
    """Orchestrates input -> update -> draw."""

    def __init__(self) -> None:
        # Inicialização do Pygame e Mixer de Áudio
        pg.mixer.pre_init(
            C.AUDIO_FREQUENCY, C.AUDIO_SIZE, C.AUDIO_CHANNELS, C.AUDIO_BUFFER
        )
        pg.init()
        pg.joystick.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Snake Multiplayer Local")

        self.clock = pg.time.Clock()
        self.running = True
        self.menu_time: float = 0.0  # Acumulador para animações do menu
        self.gameover_time: float = 0.0  # Acumulador para fade-in do game over

        # Fontes do jogo
        self.font = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_SMALL)
        self.big = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_LARGE, bold=True)

        self.renderer = Renderer(
            self.screen,
            config=C,
            fonts={"font": self.font, "big": self.big},
        )

        # Subsistemas
        self.input_manager = InputManager()
        self.lobby = Lobby(self.input_manager)
        self.world = None
        self.scene = SceneState.MENU
        self._pending_events: list = []

        # Áudio
        self.sounds = load_sounds(C.SOUND_PATH)
        self.audio = AudioManager(self.sounds)

    def run(self) -> None:
        """Big-Loop: Main runner method for Game class"""
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0

            # Atualização de tempo visual para as cenas de UI
            if self.scene == SceneState.MENU:
                self.menu_time += dt
            elif self.scene == SceneState.GAME_OVER:
                self.gameover_time += dt

            self._handle_events()
            self._update(dt)
            self._draw()

        pg.quit()

    def _handle_events(self) -> None:
        self._pending_events = pg.event.get()
        for event in self._pending_events:
            # Fechar o jogo
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                self._quit()

            # Transição: MENU -> LOBBY
            if self.scene == SceneState.MENU:
                if event.type in (pg.KEYDOWN, pg.JOYBUTTONDOWN):
                    self.lobby.reset()
                    self.scene = SceneState.LOBBY
                    self._pending_events = (
                        []
                    )  # Consome o evento para não vazar para o Lobby

            # Transição: GAME OVER -> LOBBY
            elif self.scene == SceneState.GAME_OVER:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.lobby.reset()
                    self.world = None
                    self.scene = SceneState.LOBBY
                    self._pending_events = []

            # Encaminha eventos discretos do jogo (se houver, ex: Pause no futuro)
            elif self.scene == SceneState.PLAY:
                self.input_manager.handle_gameplay_events([event])

    def _update(self, dt: float) -> None:
        # Atualização do Lobby (Retorna True quando o Countdown do ENTER acaba)
        if self.scene == SceneState.LOBBY:
            if self.lobby.update(self._pending_events, dt):
                self.world = World(self.input_manager.get_player_ids())
                self.scene = SceneState.PLAY
            return

        # Impede a atualização do World se não estiver jogando
        if self.scene != SceneState.PLAY:
            return

        # Coleta intenções de direção via Polling e atualiza o Mundo
        commands = self.input_manager.get_all_commands()
        self.world.update(dt, commands)

        # Transição: PLAY -> GAME OVER
        if self.world.game_over:
            self.audio.stop_all()
            self.gameover_time = 0.0
            self.scene = SceneState.GAME_OVER
            return

        # Toca os sons baseados nos eventos disparados pelo World (ex: "food_eaten_1")
        self.audio.play_events(self.world.events)

    def _draw(self) -> None:
        if self.scene == SceneState.MENU:
            self.renderer.draw_menu(self.menu_time)

        elif self.scene == SceneState.LOBBY:
            self.lobby.draw(self.screen, self.font, self.big)

        elif self.scene == SceneState.PLAY:
            self.renderer.clear()  # O clear do Snake desenha o Grid de fundo
            self.renderer.draw_world(self.world)
            self.renderer.draw_hud(
                self.world.scores,
                self.world.lives,
                self.scene,
                self.world.snakes,
                self.world.respawn_timers,
            )

        elif self.scene == SceneState.GAME_OVER:
            self.renderer.draw_game_over(
                scores=self.world.scores,
                elapsed=self.gameover_time,
            )

        pg.display.flip()

    def _quit(self) -> None:
        self.running = False
        pg.quit()
        sys.exit(0)
