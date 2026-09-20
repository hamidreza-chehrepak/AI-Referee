from dataclasses import dataclass


@dataclass
class GameEvent:
    player: str
    action: str


@dataclass
class PlayCardEvent(GameEvent):
    card: str

    def __init__(self, player: str, card: str):
        super().__init__(
            player=player,
            action="PLAY_CARD",
        )
        self.card = card


@dataclass
class StartGameEvent(GameEvent):

    def __init__(self):
        super().__init__(
            player="SYSTEM",
            action="START_GAME",
        )


@dataclass
class EndGameEvent(GameEvent):

    def __init__(self):
        super().__init__(
            player="SYSTEM",
            action="END_GAME",
        )