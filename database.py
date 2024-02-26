import sqlite3

class Database():
    def __init__(self):
        sqlite3.enable_callback_tracebacks(True)
        self.conn = sqlite3.connect("./data/localchess.db")
        self.conn.execute("PRAGMA foreign_keys = ON")

    def sql(self, stmt: str, arg_tuple: None|tuple = None):
        cur = self.conn.cursor()
        if type(arg_tuple) == tuple:
            res = cur.execute(stmt, arg_tuple)
        else:
            res = cur.execute(stmt)
        self.conn.commit()
        return res

    def __del__(self):
        print("Closing database")
        self.conn.close()
