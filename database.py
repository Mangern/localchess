import sqlite3

class Database():
    def __init__(self):
        self.conn = sqlite3.connect("./data/localchess.db")

    def sql(self, stmt):
        cur = self.conn.cursor()
        res = cur.execute(stmt)
        self.conn.commit()
        return res

    def __del__(self):
        print("Closing database")
        self.conn.close()
