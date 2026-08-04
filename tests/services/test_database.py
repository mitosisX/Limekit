import pytest
from lupa import LuaRuntime

from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services.database import Sqlite3


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_create_insert_fetch_round_trips_against_a_real_file(tmp_path, lua):
    path = str(tmp_path / "app.db")
    db = Sqlite3(path)
    try:
        db.createTable("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"})
        rowid = db.insert("users", {"id": 1, "name": "Alice", "age": 30})
        assert rowid == 1

        db.execute("SELECT id, name, age FROM users WHERE id = ?", (1,))
        row = convert.to_py(db.fetchOne())
        assert row == [1, "Alice", 30]

        db.execute("SELECT * FROM users")
        rows = convert.to_py(db.fetchAll(as_dict=True))
        assert rows == [{"id": 1, "name": "Alice", "age": 30}]
    finally:
        db.close()

    # Re-open the same file to prove the data was actually persisted to disk,
    # not just held in the connection's in-memory cache.
    db2 = Sqlite3(path)
    try:
        db2.execute("SELECT name FROM users WHERE id = 1")
        assert db2.fetchOne() == "Alice"
    finally:
        db2.close()


def test_execute_on_malformed_sql_raises_bridge_error(tmp_path):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        with pytest.raises(BridgeError):
            db.execute("SELECT * FROM a_table_that_does_not_exist")
    finally:
        db.close()


def test_create_table_requires_at_least_one_column(tmp_path):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        with pytest.raises(BridgeError):
            db.createTable("users", {})
    finally:
        db.close()


def test_insert_requires_at_least_one_column(tmp_path):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        db.createTable("users", {"id": "INTEGER"})
        with pytest.raises(BridgeError):
            db.insert("users", {})
    finally:
        db.close()


def test_invalid_path_raises_bridge_error():
    with pytest.raises(BridgeError):
        Sqlite3(None)
    with pytest.raises(BridgeError):
        Sqlite3("")


def test_table_exists_and_get_table_info(tmp_path, lua):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        assert db.tableExists("users") is False
        db.createTable("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        assert db.tableExists("users") is True

        info = convert.to_py(db.getTableInfo("users"))
        column_names = {col["name"] for col in info}
        assert column_names == {"id", "name"}
    finally:
        db.close()


def test_fetch_tables(tmp_path, lua):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        db.createTable("a", {"id": "INTEGER"})
        db.createTable("b", {"id": "INTEGER"})
        tables = convert.to_py(db.fetchTables())
        assert set(tables) == {"a", "b"}
    finally:
        db.close()


def test_transaction_commit_and_rollback(tmp_path, lua):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        db.createTable("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})

        db.beginTransaction()
        db.insert("users", {"id": 1, "name": "Alice"})
        db.rollback()
        db.execute("SELECT COUNT(*) FROM users")
        assert db.fetchOne() == 0

        db.beginTransaction()
        db.insert("users", {"id": 1, "name": "Alice"})
        db.commit()
        db.execute("SELECT COUNT(*) FROM users")
        assert db.fetchOne() == 1
    finally:
        db.close()


def test_execute_many(tmp_path, lua):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        db.createTable("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        db.executeMany(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            [(1, "Alice"), (2, "Bob")],
        )
        db.execute("SELECT COUNT(*) FROM users")
        assert db.fetchOne() == 2
    finally:
        db.close()


def test_backup_requires_another_sqlite3_instance(tmp_path):
    db = Sqlite3(str(tmp_path / "app.db"))
    try:
        with pytest.raises(BridgeError):
            db.backup("not a database")
    finally:
        db.close()


def test_backup_copies_data(tmp_path, lua):
    src = Sqlite3(str(tmp_path / "src.db"))
    dst = Sqlite3(str(tmp_path / "dst.db"))
    try:
        src.createTable("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        src.insert("users", {"id": 1, "name": "Alice"})
        src.backup(dst)
        dst.execute("SELECT name FROM users WHERE id = 1")
        assert dst.fetchOne() == "Alice"
    finally:
        src.close()
        dst.close()
