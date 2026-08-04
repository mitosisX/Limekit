"""SQLite3 access for Lua: `require("limekit.db")`.

Ports `limekit/core/database/sqlite3.py` (1.x `SqliteDB3`) to the 2.0
service-layer pattern (see services/fs.py). Every failure crossing the
bridge -- connection errors, malformed SQL, a locked database -- becomes a
`BridgeError`; 1.x raised its own `SqliteError`, which is not something lupa
can present usefully to a Lua script (nor is a raw `sqlite3.Error`, which
1.x also let through from `get_table_info`/`fetch_tables`/`fetchone`, none
of which had a try/except at all).

The 1.x `__enter__`/`__exit__` (Python `with` support) are dropped: Lua has
no `with` statement, so nothing could ever call them.
"""

import sqlite3

from limekit.kernel.bridge.convert import as_mapping, as_sequence, to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError


def _params(params):
    """Accept a Lua table (dict- or array-shaped) or a plain dict/sequence.

    `as_mapping` already normalises an array-shaped table into a
    {1: v1, 2: v2, ...} dict, so `.values()` yields them back in the
    original positional order either way -- one code path for both
    `db:execute("... ? ?", {30, "Alice"})` and
    `db:execute("... :age :name", {age=30, name="Alice"})`.
    """
    if params is None:
        return ()
    if isinstance(params, (list, tuple)):
        return tuple(params)
    return tuple(as_mapping(params).values())


def _rows_to_dicts(cursor, rows):
    columns = [d[0] for d in cursor.description] if cursor.description else []
    return [dict(zip(columns, row)) for row in rows]


class Sqlite3(LimeObject):
    __lime__ = "db.Sqlite3"

    def __init__(self, path=":memory:"):
        if not isinstance(path, str) or not path:
            raise BridgeError(f"expected a database path or ':memory:', got {path!r}")
        try:
            self._connection = sqlite3.connect(path, check_same_thread=False,
                                                 isolation_level=None)
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._cursor = self._connection.cursor()
        except sqlite3.Error as exc:
            raise BridgeError(f"could not open database {path!r}: {exc}") from exc
        self._in_transaction = False

    # -- transactions -----------------------------------------------------

    def beginTransaction(self):
        if not self._in_transaction:
            try:
                self._cursor.execute("BEGIN TRANSACTION")
            except sqlite3.Error as exc:
                raise BridgeError(f"could not begin transaction: {exc}") from exc
            self._in_transaction = True
        return self

    def commit(self):
        if self._in_transaction:
            try:
                self._connection.commit()
            except sqlite3.Error as exc:
                raise BridgeError(f"could not commit: {exc}") from exc
            self._in_transaction = False
        return self

    def rollback(self):
        if self._in_transaction:
            try:
                self._connection.rollback()
            except sqlite3.Error as exc:
                raise BridgeError(f"could not roll back: {exc}") from exc
            self._in_transaction = False
        return self

    def save(self):
        """Alias for commit()."""
        return self.commit()

    # -- queries ------------------------------------------------------------

    def execute(self, query, params=None):
        if not isinstance(query, str) or not query:
            raise BridgeError(f"expected a non-empty SQL string, got {query!r}")
        try:
            self._cursor.execute(query, _params(params))
        except sqlite3.OperationalError as exc:
            if "database is locked" in str(exc):
                raise BridgeError("database locked - please try again later") from exc
            raise BridgeError(f"operational error: {exc}") from exc
        except sqlite3.Error as exc:
            raise BridgeError(f"failed to execute query: {exc}") from exc
        return self

    def executeMany(self, query, data):
        if not isinstance(query, str) or not query:
            raise BridgeError(f"expected a non-empty SQL string, got {query!r}")
        try:
            tuple_rows = [_params(row) for row in as_sequence(data)]
            self._cursor.executemany(query, tuple_rows)
        except sqlite3.Error as exc:
            raise BridgeError(f"failed to execute multiple queries: {exc}") from exc
        return self

    def fetchAll(self, as_dict=False):
        try:
            rows = self._cursor.fetchall()
        except sqlite3.Error as exc:
            raise BridgeError(f"failed to fetch data: {exc}") from exc
        if as_dict:
            return to_lua(_rows_to_dicts(self._cursor, rows))
        return to_lua([list(row) for row in rows])

    def fetchOne(self, as_dict=False):
        try:
            row = self._cursor.fetchone()
        except sqlite3.Error as exc:
            raise BridgeError(f"failed to fetch data: {exc}") from exc
        if row is None:
            return None
        if as_dict:
            columns = [d[0] for d in self._cursor.description]
            return to_lua(dict(zip(columns, row)))
        return to_lua(row[0] if len(row) == 1 else list(row))

    def fetchTables(self):
        try:
            self._cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            )
            tables = [row[0] for row in self._cursor.fetchall()]
        except sqlite3.Error as exc:
            raise BridgeError(f"could not list tables: {exc}") from exc
        return to_lua(tables)

    def tableExists(self, table_name):
        if not isinstance(table_name, str) or not table_name:
            raise BridgeError(f"expected a table name, got {table_name!r}")
        try:
            self._cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,),
            )
            return self._cursor.fetchone() is not None
        except sqlite3.Error as exc:
            raise BridgeError(f"could not check table {table_name!r}: {exc}") from exc

    def getTableInfo(self, table_name):
        if not isinstance(table_name, str) or not table_name:
            raise BridgeError(f"expected a table name, got {table_name!r}")
        try:
            self._cursor.execute(f"PRAGMA table_info({table_name});")
            rows = self._cursor.fetchall()
        except sqlite3.Error as exc:
            raise BridgeError(f"could not inspect table {table_name!r}: {exc}") from exc
        return to_lua(_rows_to_dicts(self._cursor, rows))

    def createTable(self, table_name, columns, if_not_exists=True):
        if not isinstance(table_name, str) or not table_name:
            raise BridgeError(f"expected a table name, got {table_name!r}")
        column_items = list(as_mapping(columns).items())
        if not column_items:
            raise BridgeError("createTable requires at least one column")

        clause = "IF NOT EXISTS " if if_not_exists else ""
        columns_sql = ", ".join(f"{name} {defn}" for name, defn in column_items)
        self.execute(f"CREATE TABLE {clause}{table_name} ({columns_sql});")
        return self

    def insert(self, table_name, data, replace=False):
        if not isinstance(table_name, str) or not table_name:
            raise BridgeError(f"expected a table name, got {table_name!r}")
        items = list(as_mapping(data).items())
        if not items:
            raise BridgeError("insert requires at least one column/value pair")

        operation = "REPLACE" if replace else "INSERT"
        columns = ", ".join(str(name) for name, _ in items)
        placeholders = ", ".join(["?"] * len(items))
        values = tuple(value for _, value in items)

        query = f"{operation} INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute(query, values)
        return self._cursor.lastrowid

    def vacuum(self):
        self.execute("VACUUM")
        return self

    def backup(self, target):
        if not isinstance(target, Sqlite3):
            raise BridgeError(f"expected another db.Sqlite3, got {target!r}")
        try:
            self._connection.backup(target._connection)
        except sqlite3.Error as exc:
            raise BridgeError(f"backup failed: {exc}") from exc
        return self

    def close(self):
        if self._in_transaction:
            self.rollback()
        self._connection.close()
        return self
