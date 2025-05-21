import sqlite3
from typing import Optional, Union, List, Dict, Any, Tuple
from limekit.engine.parts import EnginePart
from limekit.utils.converters import Converter


class SqliteDB3(EnginePart):
    """
    An advanced SQLite3 database wrapper with extended functionality.

    Example Usage:
        db = SqliteDB3("mydatabase.db")
        db.create_table("users", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "email": "TEXT UNIQUE"
        })
        user_id = db.insert("users", {"name": "Alice", "email": "alice@example.com"})
        users = db.fetchall("SELECT * FROM users")
        db.close()
    """

    name = "Sqlite3"

    def __init__(self, db: str = "") -> None:
        """
        Initialize the SQLite database connection.

        Args:
            db: Database file path or ":memory:" for in-memory database

        Example:
            # Disk-based database
            db = SqliteDB3("my_database.db")

            # In-memory database
            db = SqliteDB3(":memory:")
        """
        try:
            if db == ":memory:":
                self.connection = sqlite3.connect(
                    ":memory:", check_same_thread=False, isolation_level=None
                )
            else:
                self.connection = sqlite3.connect(
                    db, check_same_thread=False, isolation_level=None
                )

            # Enable foreign key constraints by default
            self.connection.execute("PRAGMA foreign_keys = ON")

            # Use row factory for named tuple access
            self.connection.row_factory = sqlite3.Row

            self.command = self.connection.cursor()
            self._in_transaction = False

        except sqlite3.Error as e:
            raise SqliteError(f"Failed to connect to database: {str(e)}")

    def begin_transaction(self) -> None:
        """
        Begin a new transaction.

        Example:
            db.begin_transaction()
            try:
                db.insert("accounts", {"id": 1, "balance": 100})
                db.insert("transactions", {"account_id": 1, "amount": 100})
                db.commit()
            except:
                db.rollback()
        """
        if not self._in_transaction:
            self.command.execute("BEGIN TRANSACTION")
            self._in_transaction = True

    def commit(self) -> None:
        """
        Commit the current transaction.

        Example:
            db.begin_transaction()
            db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
            db.commit()
        """
        if self._in_transaction:
            self.connection.commit()
            self._in_transaction = False

    def rollback(self) -> None:
        """
        Roll back the current transaction.

        Example:
            db.begin_transaction()
            try:
                # Operations that might fail
                db.commit()
            except Exception as e:
                db.rollback()
                print("Transaction failed:", e)
        """
        if self._in_transaction:
            self.connection.rollback()
            self._in_transaction = False

    def save(self) -> None:
        """
        Alias for commit().
        """
        self.commit()

    def execute(self, query: str, params: Optional[Union[Dict, Tuple]] = None) -> None:
        """
        Execute a single SQL query.

        Args:
            query: SQL query string with ? placeholders
            params: Parameters for the query (dict or tuple)

        Example with tuple params:
            db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 30))
            # Executes: INSERT INTO users (name, age) VALUES ('Alice', 30)

        Example with dict params:
            db.execute("INSERT INTO users (name, age) VALUES (:name, :age)",
                      {"name": "Bob", "age": 25})
            # Executes: INSERT INTO users (name, age) VALUES ('Bob', 25)
        """
        try:
            if isinstance(params, dict):
                self.command.execute(query, tuple(params.values()))
            elif params:
                self.command.execute(query, params)
            else:
                self.command.execute(query)

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                raise SqliteError("Database locked - please try again later")
            raise SqliteError(f"Operational error: {str(e)}")
        except sqlite3.Error as e:
            raise SqliteError(f"Failed to execute query: {str(e)}")

    def executemany(self, query: str, data: List[Union[Tuple, Dict]]) -> None:
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query string with ? placeholders
            data: List of parameter sets (tuples or dicts)

        Example with tuple params:
            data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
            db.executemany("INSERT INTO users (name, age) VALUES (?, ?)", data)
            # Executes 3 inserts with the provided values

        Example with dict params:
            data = [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35}
            ]
            db.executemany("INSERT INTO users (name, age) VALUES (:name, :age)", data)
        """
        try:
            if data and isinstance(data[0], dict):
                # Convert list of dicts to list of tuples
                param_keys = data[0].keys()
                tuple_data = [tuple(item[key] for key in param_keys) for item in data]
                self.command.executemany(query, tuple_data)
            else:
                self.command.executemany(query, data)

        except sqlite3.Error as e:
            raise SqliteError(f"Failed to execute multiple queries: {str(e)}")

    def fetchall(self, as_dict: bool = False) -> Union[List[Tuple], List[Dict]]:
        """
        Fetch all rows from the last executed query.

        Args:
            as_dict: If True, return rows as dictionaries

        Example:
            db.execute("SELECT * FROM users WHERE age > ?", (25,))
            # SQL executed: SELECT * FROM users WHERE age > 25

            rows = db.fetchall()
            # Returns: [(1, 'Alice', 30), (3, 'Charlie', 35)]

            rows = db.fetchall(as_dict=True)
            # Returns: [{'id': 1, 'name': 'Alice', 'age': 30},
            #           {'id': 3, 'name': 'Charlie', 'age': 35}]
        """
        try:
            fetched_data = self.command.fetchall()

            if as_dict:
                return [dict(row) for row in fetched_data]

            # Convert to Lua table if needed
            lua_table = []
            for sublist in fetched_data:
                lua_table.append(sublist)

            return Converter.table_from(*lua_table)

        except sqlite3.Error as e:
            raise SqliteError(f"Failed to fetch data: {str(e)}")

    def fetchone(self, as_dict: bool = False) -> Optional[Union[Tuple, Dict]]:
        """
        Fetch a single row from the last executed query.

        Args:
            as_dict: If True, return row as dictionary

        Example:
            db.execute("SELECT * FROM users WHERE id = ?", (1,))
            # SQL executed: SELECT * FROM users WHERE id = 1

            row = db.fetchone()
            # Returns: (1, 'Alice', 30)

            row = db.fetchone(as_dict=True)
            # Returns: {'id': 1, 'name': 'Alice', 'age': 30}
        """
        row = self.command.fetchone()
        if row is None:
            return None

        return dict(row) if as_dict else row[0] if len(row) == 1 else row

    def fetch_tables(self) -> List[str]:
        """
        Get a list of all tables in the database.

        Example:
            tables = db.fetch_tables()
            # Returns: ['users', 'products', 'orders']
            # SQL executed: SELECT name FROM sqlite_master
            #              WHERE type="table" AND name NOT LIKE "sqlite_%"
        """
        self.command.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%";'
        )
        tables = [table[0] for table in self.command.fetchall()]
        return Converter.table_from(tables)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Example:
            if db.table_exists("users"):
                print("Users table exists")
            # SQL executed: SELECT name FROM sqlite_master
            #               WHERE type='table' AND name='users'
        """
        self.command.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        return self.command.fetchone() is not None

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's columns.

        Args:
            table_name: Name of the table

        Example:
            columns = db.get_table_info("users")
            # Returns: [{'cid': 0, 'name': 'id', 'type': 'INTEGER', 'notnull': 0, ...},
            #           {'cid': 1, 'name': 'name', 'type': 'TEXT', 'notnull': 1, ...}]
            # SQL executed: PRAGMA table_info(users)
        """
        self.command.execute(f"PRAGMA table_info({table_name});")
        return [dict(row) for row in self.command.fetchall()]

    def create_table(
        self, table_name: str, columns: Dict[str, str], if_not_exists: bool = True
    ) -> None:
        """
        Create a new table.

        Args:
            table_name: Name of the new table
            columns: Dictionary of column names and SQL type definitions
            if_not_exists: If True, adds IF NOT EXISTS clause

        Example:
            db.create_table("users", {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "TEXT NOT NULL",
                "age": "INTEGER",
                "email": "TEXT UNIQUE"
            })
            # SQL executed: CREATE TABLE IF NOT EXISTS users (
            #               id INTEGER PRIMARY KEY AUTOINCREMENT,
            #               name TEXT NOT NULL,
            #               age INTEGER,
            #               email TEXT UNIQUE)
        """
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        columns_sql = ", ".join([f"{name} {defn}" for name, defn in columns.items()])

        query = f"CREATE TABLE {if_not_exists_clause}{table_name} ({columns_sql});"
        self.execute(query)

    def insert(
        self, table_name: str, data: Dict[str, Any], replace: bool = False
    ) -> int:
        """
        Insert a new row into a table.

        Args:
            table_name: Name of the table
            data: Dictionary of column names and values
            replace: If True, use REPLACE instead of INSERT

        Returns:
            The rowid of the inserted row

        Example:
            user_id = db.insert("users", {
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com"
            })
            # SQL executed: INSERT INTO users (name, age, email)
            #                VALUES ('Alice', 30, 'alice@example.com')

            # With replace=True
            db.insert("users", {"id": 1, "name": "Alice"}, replace=True)
            # SQL executed: REPLACE INTO users (id, name) VALUES (1, 'Alice')
        """
        operation = "REPLACE" if replace else "INSERT"
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))

        query = f"{operation} INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute(query, data)

        return self.command.lastrowid

    def close(self) -> None:
        """
        Close the database connection.

        Example:
            db = SqliteDB3("mydb.db")
            try:
                # Database operations
            finally:
                db.close()
        """
        if self._in_transaction:
            self.rollback()

        self.connection.close()

    def __enter__(self):
        """Support for context manager (with statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self.close()

    def backup(self, target_db: "SqliteDB3") -> None:
        """
        Backup the current database to another database.

        Args:
            target_db: Another SqliteDB3 instance to backup to

        Example:
            main_db = SqliteDB3("main.db")
            backup_db = SqliteDB3("backup.db")
            main_db.backup(backup_db)
        """
        self.connection.backup(target_db.connection)

    def vacuum(self) -> None:
        """
        Rebuild the database file, repacking it into minimal disk space.

        Example:
            db.vacuum()
            # SQL executed: VACUUM
        """
        self.execute("VACUUM")


class SqliteError(Exception):
    """Custom exception for SQLite operations."""

    pass
