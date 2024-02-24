from dataclasses import dataclass
import datetime
import sqlite3

from database import Database

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

                FOREIGN KEY (white_id) REFERENCES player(player_id),
                FOREIGN KEY (black_id) REFERENCES player(player_id)
            )
        """)



