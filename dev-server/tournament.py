from dataclasses import dataclass
from datetime import datetime
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
                time_end_iso TEXT,
                active INTEGER NOT NULL
            )
        """)

        self.tp_table = TournamentPlayerTable(self.db)

        self.active_tournament = None

    def __getitem__(self, tournament_id: int) -> Optional[Tournament]:
        stmt = """
            SELECT tournament_id, tournament_name, time_start_iso, active FROM tournament where tournament_id = ?
        """
        row = self.db.sql(stmt, (tournament_id,)).fetchone()
        if row is None:
            return None
        return Tournament(row[0], row[1], row[2], row[3] != 0)

    def get_active_id(self) -> Optional[int]:
        if self.active_tournament is not None:
            return self.active_tournament

        stmt = """
            SELECT tournament_id FROM tournament WHERE active <> 0
        """

        result = self.db.sql(stmt).fetchone()

        if result is None:
            self.active_tournament = None
            return None

        self.active_tournament = result[0]
        return result[0]

    def add_player_to_active(self, player_id: int):
        if self.active_tournament is None:
            return

        self.tp_table.add_player_to_tournament(player_id, self.active_tournament)

    def get_active_scoreboard(self):
        return []

    def start_tournament(self, tournament_name: str):
        if self.get_active_id() is not None:
            return

        stmt = """
            INSERT INTO tournament (tournament_name, time_start_iso, active) VALUES (?, ?, ?)
        """

        self.db.sql(stmt, (tournament_name, datetime.now().isoformat(), 1))

    def end_active_tournament(self):
        active_id = self.get_active_id()
        if active_id is None:
            return
        
        end_time = datetime.now().isoformat()

        stmt = """
            UPDATE tournament SET time_end_iso = ?, active = 0 WHERE tournament_id = ?
        """

        self.db.sql(stmt, (end_time, active_id))


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

