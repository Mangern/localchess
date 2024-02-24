
from dataclasses import dataclass

@dataclass
class Player:
    id: int
    name: str

class LocalChess:
    def __init__(self):
        self.players = [
            Player(0, "Alan"), 
            Player(1, "Donald"), 
            Player(2, "Brian"),
            Player(3, "Edgar"),
            Player(4, "Dennis"),
        ]

    def dictify(self, data: list|dict|Player):
        if type(data) == list:
            return [self.dictify(x) for x in data]
        elif type(data) == dict:
            return {k: self.dictify(v) for k, v in data.items()}
        elif type(data) == Player:
            return data.__dict__
        else:
            assert False, "Exhaustive implementation of types in dictify"

    def get_players(self):
        return self.dictify(self.players)

    def register_result(self, white_id, black_id, result_str):
        print(white_id, black_id, result_str)
