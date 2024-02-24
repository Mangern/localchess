from dataclasses import dataclass
import sqlite3

from database import Database

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
                name text NOT NULL,
                elo REAL DEFAULT 1200.0
            )
        """)

    def get_all(self):
        stmt = """
            SELECT player_id, name, elo FROM player
        """
        res = self.db.sql(stmt)

        player_list = []

        for row in res:
            player_list.append(Player(*row))

        return player_list
