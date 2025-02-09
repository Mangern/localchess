from dataclasses import dataclass
import datetime

from database import Database

from constants import ELO_K

@dataclass
class Game:
    id: int
    white_id: int
    black_id: int
    result: int
    elo_white: float
    elo_black: float
    timestamp_iso: str 

    def to_dict(self):
        return self.__dict__

class GameTable:
    def __init__(self, db: Database):
        self.db = db


        self.db.sql("""
            CREATE TABLE IF NOT EXISTS game (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                white_id INTEGER NOT NULL,
                black_id INTEGER NOT NULL,
                result INTEGER NOT NULL,
                elo_white REAL NOT NULL,
                elo_black REAL NOT NULL,
                timestamp_iso TEXT,
                tournament_id INTEGER,

                FOREIGN KEY (white_id) REFERENCES player(player_id),
                FOREIGN KEY (black_id) REFERENCES player(player_id),
                FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
            )
        """)


    def register_game(self, 
        white_id: int, 
        black_id: int, 
        white_elo: float, 
        black_elo: float, 
        result: str|int,
        tournament_id: int|None) -> tuple[float,float]:

        if type(result) == str:
            if result == "white":
                result = 1
            elif result == "black":
                result = -1
            else:
                result = 0


        score_white = 1 if result == 1 else 0
        score_black = 1 if result == -1 else 0

        if result == 0:
            score_white = 0.5
            score_black = 0.5

        expect_white = 1 / (1 + 10**((black_elo - white_elo) / 400))
        expect_black = 1 / (1 + 10**((white_elo - black_elo) / 400))

        new_white_elo = white_elo + ELO_K * (score_white - expect_white)
        new_black_elo = black_elo + ELO_K * (score_black - expect_black)

        current_time = datetime.datetime.now().isoformat()

        stmt = """
            INSERT INTO game (
                white_id,
                black_id,
                result,
                elo_white,
                elo_black,
                timestamp_iso,
                tournament_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.db.sql(stmt, (
            white_id,
            black_id,
            result,
            new_white_elo,
            new_black_elo,
            current_time,
            tournament_id
        ))

        return new_white_elo, new_black_elo

    def get_all(self) -> list[Game]:
        stmt = """
            SELECT game_id, white_id, black_id, result, elo_white, elo_black, timestamp_iso FROM game
        """

        res = self.db.sql(stmt)
        return [Game(*row) for row in res]
    
    def games_of_player(self, player_id: int) -> list[Game]:
        stmt = """
            SELECT game_id, white_id, black_id, result, elo_white, elo_black, timestamp_iso FROM game WHERE (white_id = ?) OR (black_id = ?)
        """

        res = self.db.sql(stmt, (player_id, player_id))
        return [Game(*row) for row in res]

    def get_tournament_games(self, tournament_id: int) -> list[Game]:
        stmt = """
            SELECT game_id, white_id, black_id, result, elo_white, elo_black, timestamp_iso FROM game WHERE tournament_id = ?
        """

        res = self.db.sql(stmt, (tournament_id, ))

        return [Game(*row) for row in res]
