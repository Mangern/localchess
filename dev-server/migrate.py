from dataclasses import dataclass
from threading import local
from localchess import LocalChess

@dataclass
class HistoryLine:
    white: str
    black: str
    res_white: float
    res_black: float
    elo_white: float
    elo_black: float
    timestamp_iso: str


if __name__ == "__main__":
    localchess = LocalChess()
    players = set()
    history_lines_txt = open("../classic/history.txt").read().splitlines()
    history_lines: list[HistoryLine] = []
    for line in history_lines_txt:
        toks = line.split()
        history_lines.append(HistoryLine(
            toks[0],
            toks[1],
            float(toks[2]),
            float(toks[3]),
            float(toks[4][1:-1]),
            float(toks[7][1:-1]),
            toks[-1]
        ))

    for line in history_lines:
        if line.white not in players:
            players.add(line.white)
            localchess.player_table.add_player(line.white)
            id = localchess.player_table.get_id(line.white)
            assert id is not None
            localchess.player_table.set_elo(id, line.elo_white)
        if line.black not in players:
            players.add(line.black)
            localchess.player_table.add_player(line.black)
            id = localchess.player_table.get_id(line.black)
            assert id is not None
            localchess.player_table.set_elo(id, line.elo_black)

    for line in history_lines:
        id_white = localchess.player_table.get_id(line.white)
        assert id_white is not None
        id_black = localchess.player_table.get_id(line.black)
        assert id_black is not None

        elo_white = localchess.player_table.get_elo(id_white)
        elo_black = localchess.player_table.get_elo(id_black)

        result = 1 if abs(line.res_white - 1.0) < 1e-6 else -1 if abs(line.res_black - 1.0) < 1e-6 else 0

        localchess.game_table.register_game(id_white, id_black, elo_white, elo_black, result, None)
        localchess.player_table.set_elo(id_white, elo_white)
        localchess.player_table.set_elo(id_black, elo_black)
