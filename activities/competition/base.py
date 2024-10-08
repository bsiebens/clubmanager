from typing import TypedDict
from ..models import Game


class GameInformation(TypedDict):
    live: bool
    scoreA: int
    scoreB: int


class CompetitionBaseClass:
    url: str

    def __init__(self):
        self.url = "http://localhost"

    def update_game_information(self, game: Game) -> None:
        raise NotImplementedError
