from typing import Optional, TypeAlias
from database import Database

from game import GameTable, Game
from player import PlayerTable, Player
from tournament import Tournament, TournamentTable

atomic: TypeAlias = str|int|bool|float

def atomic_type(x: any) -> bool:
    return type(x) in [str,int,bool,float]

class LocalChess:
    def __init__(self):
        self.db = Database()
        self.player_table = PlayerTable(self.db)
        self.game_table = GameTable(self.db)
        self.tournament_table = TournamentTable(self.db)
        self.content_change = True

    # TODO fix some of this ugly ass shit
    def json_serializable(self, data: Optional[atomic|list|dict|Player|Game|Tournament]) -> Optional[atomic|dict|list|int]:
        if data is None:
            return None
        elif atomic_type(data):
            return data
        elif type(data) == list:
            return [self.json_serializable(x) for x in data]
        elif type(data) == dict:
            return {k: self.json_serializable(v) for k, v in data.items()}
        elif type(data) == Player:
            return data.to_dict()
        elif type(data) == Game:
            return data.to_dict()
        elif type(data) == Tournament:
            return data.to_dict()
        else:
            assert False, "Exhaustive implementation of types in dictify"

    def content_did_change(self) -> bool:
        return self.content_change

    def get_players(self):
        return self.json_serializable(self.player_table.get_all())

    def get_full_game_state(self):
        active_tournament = self.tournament_table.get_active()
        game_state = {
            "players": self.get_players(),
            "active_tournament": active_tournament
        }

        if active_tournament is not None:
            game_state["tournament_data"] = self.tournament_table.get_active_scoreboard()

        return self.json_serializable(game_state)

    def register_result(self, white_id, black_id, result_str):
        result_str = result_str.lower()
        old_white_elo = self.player_table.get_elo(white_id)
        old_black_elo = self.player_table.get_elo(black_id)
        active_tourney = self.tournament_table.get_active()
        print(white_id, black_id, result_str)
        white_elo, black_elo = self.game_table.register_game(
            white_id      = white_id,
            black_id      = black_id,
            white_elo     = old_white_elo,
            black_elo     = old_black_elo,
            result        = 0 if result_str == "remis" else (1 if result_str == "white" else -1),
            tournament_id = active_tourney
        )

        self.player_table.set_elo(white_id, white_elo)
        self.player_table.set_elo(black_id, black_elo)
        self.content_change = True

