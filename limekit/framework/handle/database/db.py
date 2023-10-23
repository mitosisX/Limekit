import sqlite3
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class Sqlite3(EnginePart):
    def __init__(self, db=""):
        if db == ":memory:":
            self.connection = sqlite3.connect(":memory:")
        else:
            self.connection = sqlite3.connect(db)

        self.command = self.connection.cursor()

    def save(self):
        self.connection.commit()

    def execute(self, query, params=None):
        try:
            self.command.execute(query, tuple(params.values()) if params else ())
        except sqlite3.OperationalError:
            print("Failed: Database locked")

    # data = [
    #   ('2006-03-28', 'BUY', 'IBM', 1000, 45.0),
    #   ('2006-04-05', 'BUY', 'MSFT', 1000, 72.0),
    #   ('2006-04-06', 'SELL', 'IBM', 500, 53.0),
    #  ]
    # >>> cur.executemany('INSERT INTO stocks VALUES(?, ?, ?, ?, ?)', data)
    def executeMany(self, data):
        pass

    def fetchAll(self):
        fetched_data = self.command.fetchall()

        lua_table = []

        # Iterate through the Python list of lists and add them to the Lua table
        for sublist in fetched_data:
            lua_table.append(sublist)

        # print(lua_table)

        return Converter.table_from(*lua_table)

    # The result is always like (1,). What's the tuple for anyway?
    def fetchOne(self):
        return self.command.fetchone()[0]

    def process_fectch(self):
        pass

    def fetchTables(self):
        tables = []
        self.command.execute('SELECT * FROM sqlite_master where type="table";')

        for table in self.command.fetchall():
            each_table = table[1]
            # if "sqlite_sequence" not in each_table:
            tables.append(each_table)

        return Converter.table_from(tables)

    def close(self):
        self.connection.close()
