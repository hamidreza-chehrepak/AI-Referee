from dataclasses import dataclass, field


@dataclass
class GameState:
    player1: str
    player2: str
    player1_cards: list[str] = field(default_factory=list)
    player2_cards: list[str] = field(default_factory=list)
    trump: str | None = None
    current_turn: str | None = None
    cards_played: list[str] = field(default_factory=list)
    score_player1: int = 0
    score_player2: int = 0
    round_number: int = 1