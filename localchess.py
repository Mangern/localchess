from dataclasses import dataclass
from database import Database

from game import GameTable, Game
from player import PlayerTable, Player


class LocalChess:
    def __init__(self):
        self.db = Database()
        self.player_table = PlayerTable(self.db)
        self.game_table = GameTable(self.db)

    def dictify(self, data: list|dict|Player):
        if type(data) == list:
            return [self.dictify(x) for x in data]
        elif type(data) == dict:
            return {k: self.dictify(v) for k, v in data.items()}
        elif type(data) == Player:
            return data.to_dict()
        elif type(data) == Game:
            return data.to_dict()
        else:
            assert False, "Exhaustive implementation of types in dictify"

    def get_players(self):
        return self.dictify(self.player_table.get_all())

    def register_result(self, white_id, black_id, result_str):
        print(white_id, black_id, result_str)
