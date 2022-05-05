import sqlite3


class DataBase:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()

    def select_with_fetchone(self, cmd):
        self.cur.execute(cmd)
        result = self.cur.fetchone()
        return result

    def select_with_fetchall(self, cmd):
        self.cur.execute(cmd)
        result = self.cur.fetchall()
        return result

    def query(self, cmd):
        self.cur.execute(cmd)
        self.con.commit()
