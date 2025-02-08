from dataclasses import dataclass
import sqlite3

from database import Database
from constants import DEFAULT_ELO

@dataclass
class Player:
    id: int
    name: str
    elo: float

    def to_dict(self):
        return self.__dict__


class PlayerTable:
    def __init__(self, db: Database):
        self.db = db

        self.db.sql("""
            CREATE TABLE IF NOT EXISTS player (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name text NOT NULL UNIQUE,
                elo REAL DEFAULT 1200.0
            )
        """)

    def __getitem__(self, player_id: int) -> Player | None:
        assert type(player_id) == int
        stmt = """
            SELECT player_id, player_name, elo FROM player WHERE player_id = ?
        """
        res = self.db.sql(stmt, (player_id,)).fetchone()
        if res is None:
            return None
        return Player(*res)

    def get_all(self) -> list[Player]:
        stmt = """
            SELECT player_id, player_name, elo FROM player
        """
        res = self.db.sql(stmt)

        player_list = []

        for row in res:
            player_list.append(Player(*row))

        return player_list

    def get_elo(self, player_id: int) -> float:
        stmt = """
            SELECT elo FROM player WHERE player_id = ?
        """

        result = self.db.sql(stmt, (player_id,)).fetchone()
        return result[0]

    def set_elo(self, player_id: int, new_elo: float):
        stmt = """
            UPDATE player SET elo = ? WHERE player_id = ?
        """

        self.db.sql(stmt, (new_elo, player_id))

    def get_id(self, player_name: str) -> int | None:
        stmt = """
            SELECT player_id FROM player WHERE player_name = ?
        """

        res = self.db.sql(stmt, (player_name,)).fetchone()
        if res is None:
            return None
        return res[0]

    def player_exists(self, player_name: str) -> bool:
        player_name = player_name.lower().strip()
        stmt = """
            SELECT player_id FROM player WHERE player_name = ? LIMIT 1
        """

        res = self.db.sql(stmt, (player_name,))
        for row in res:
            return True
        return False


    def add_player(self, player_name: str) -> bool:
        player_name = player_name.lower().strip()
        print("Adding:", player_name)
        if self.player_exists(player_name):
            return False
        stmt = """
            INSERT INTO player (player_name, elo) VALUES (?, ?)
        """

        ret = self.db.sql(stmt, (player_name, DEFAULT_ELO))
        if ret.lastrowid is None:
            return False
        return True
