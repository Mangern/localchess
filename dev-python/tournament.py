from dataclasses import dataclass
from typing import Optional

from database import Database


@dataclass
class Tournament:
    id: int
    name: int
    time_start_iso: str
    active: bool

    def to_dict(self):
        return self.__dict__

class TournamentTable:
    def __init__(self, db: Database):
        self.db = db


        self.db.sql("""
            CREATE TABLE IF NOT EXISTS tournament (
                tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_name TEXT NOT NULL,
                time_start_iso TEXT NOT NULL,
                time_end_iso TEXT NOT NULL,
                active INTEGER NOT NULL
            )
        """)

        self.tp_table = TournamentPlayerTable(self.db)

        self.active_tournament = None

    def get_active(self) -> Optional[int]:
        if self.active_tournament is not None:
            return self.active_tournament

        stmt = """
            SELECT tournament_id FROM tournament WHERE active <> 0
        """

        result = self.db.sql(stmt).fetchone()
        self.active_tournament = result

        if result is None:
            return None

        return result["tournament_id"]

    def add_player_to_active(self, player_id: int):
        if self.active_tournament is None:
            return

        self.tp_table.add_player_to_tournament(player_id, self.active_tournament)

    def get_active_scoreboard(self):
        return []


class TournamentPlayerTable:
    def __init__(self, db: Database):
        self.db = db

        self.db.sql("""
            CREATE TABLE IF NOT EXISTS tournament_has_player (
                player_id INTEGER NOT NULL,
                tournament_id INTEGER NOT NULL,
                PRIMARY KEY (tournament_id, player_id),
                FOREIGN KEY (tournament_id) REFERENCES tournament (tournament_id),
                FOREIGN KEY (player_id) REFERENCES player (player_id)
            )
        """)

    def add_player_to_tournament(self, player_id: int, tournament_id: int):
        stmt = """
            INSERT INTO tournament_has_player (
                tournament_id,
                player_id
            ) VALUES (?, ?)
        """

        self.db.sql(stmt, (tournament_id, player_id))
