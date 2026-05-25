"""Audio playback manager for the Snake game client."""

import pygame as pg

from client.audio.pack import SoundPack


class AudioManager:
    """Gerencia a reprodução de efeitos sonoros baseados em eventos do World."""

    def __init__(self, sounds: SoundPack) -> None:
        self.sounds = sounds

    def play_events(self, events: list[str]) -> None:
        """Lê a lista de eventos do frame e dispara os sons correspondentes."""
        for ev in events:
            if ev == "snake_hit_wall":
                self.sounds.hit_boundary.play()
            elif ev in ("snake_hit_self", "snake_pvp_kill"):
                self.sounds.hit_player.play()
            elif ev.startswith("food_eaten_"):
                # Extrai o ID do jogador da string de evento (ex: "food_eaten_1")
                try:
                    player_id = int(ev.split("_")[-1])
                    # Jogadores 1 e 3 usam o som 1; Jogadores 2 e 4 usam o som 2
                    if player_id in (1, 3):
                        self.sounds.eat_1.play()
                    else:
                        self.sounds.eat_2.play()
                except ValueError:
                    print(
                        f"[ERROR]: SoundManager - Could not retrieve Player ID from: {ev}"
                    )
                    self.sounds.eat_2.play()

    def stop_all(self) -> None:
        """Para todos os canais de som ativos (Útil para o Game Over)."""
        pg.mixer.stop()
