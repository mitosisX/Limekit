import pytest
from lupa import LuaRuntime

from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services.fs import FileSystem


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_write_then_read_round_trips(tmp_path):
    path = str(tmp_path / "a.txt")
    assert FileSystem.writeFile(path, "hello") is True
    assert FileSystem.readFile(path) == "hello"


def test_append_file(tmp_path):
    path = str(tmp_path / "a.txt")
    FileSystem.writeFile(path, "hello")
    FileSystem.appendFile(path, " world")
    assert FileSystem.readFile(path) == "hello world"


def test_create_file(tmp_path):
    path = str(tmp_path / "new.txt")
    assert FileSystem.createFile(path) is True
    assert FileSystem.exists(path) is True
    assert FileSystem.isFileEmpty(path) is True


def test_create_file_that_already_exists_raises_bridge_error(tmp_path):
    path = str(tmp_path / "new.txt")
    FileSystem.createFile(path)
    with pytest.raises(BridgeError):
        FileSystem.createFile(path)


def test_delete_file(tmp_path):
    path = str(tmp_path / "a.txt")
    FileSystem.writeFile(path, "x")
    assert FileSystem.deleteFile(path) is True
    assert FileSystem.exists(path) is False


def test_delete_missing_file_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.deleteFile(str(tmp_path / "missing.txt"))


def test_copy_file(tmp_path):
    src = str(tmp_path / "a.txt")
    dst = str(tmp_path / "b.txt")
    FileSystem.writeFile(src, "content")
    assert FileSystem.copyFile(src, dst) is True
    assert FileSystem.readFile(dst) == "content"


def test_copy_missing_file_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.copyFile(str(tmp_path / "missing.txt"), str(tmp_path / "b.txt"))


def test_rename_file(tmp_path):
    src = str(tmp_path / "a.txt")
    dst = str(tmp_path / "b.txt")
    FileSystem.writeFile(src, "content")
    assert FileSystem.renameFile(src, dst) is True
    assert FileSystem.exists(dst) is True
    assert FileSystem.exists(src) is False


def test_rename_missing_file_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.renameFile(str(tmp_path / "missing.txt"), str(tmp_path / "b.txt"))


def test_exists_and_is_folder(tmp_path):
    assert FileSystem.exists(str(tmp_path)) is True
    assert FileSystem.isFolder(str(tmp_path)) is True
    assert FileSystem.isFolder(str(tmp_path / "nope")) is False


def test_get_file_name_size_ext(tmp_path):
    path = str(tmp_path / "a.txt")
    FileSystem.writeFile(path, "hello")
    assert FileSystem.getFileName(path) == "a.txt"
    assert FileSystem.getFileSize(path) == 5
    assert FileSystem.getFileExt(path) == ".txt"


def test_get_file_size_missing_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.getFileSize(str(tmp_path / "missing.txt"))


def test_create_and_list_folder(tmp_path, lua):
    folder = str(tmp_path / "sub")
    assert FileSystem.createFolder(folder) is True
    FileSystem.writeFile(str(tmp_path / "sub" / "a.txt"), "x")
    listed = FileSystem.listFolder(folder)
    assert convert.to_py(listed) == ["a.txt"]


def test_list_missing_folder_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.listFolder(str(tmp_path / "missing"))


def test_walk_dir(tmp_path, lua):
    (tmp_path / "sub").mkdir()
    FileSystem.writeFile(str(tmp_path / "a.txt"), "x")
    result = convert.to_py(FileSystem.walkDir(str(tmp_path)))
    names = {entry["name"] for entry in result}
    assert names == {"sub", "a.txt"}


def test_walk_dir_missing_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.walkDir(str(tmp_path / "missing"))


def test_join_normal_dirname_paths(tmp_path):
    joined = FileSystem.joinPaths(str(tmp_path), "a", "b.txt")
    assert joined.endswith("b.txt")
    assert FileSystem.getDirName(joined) == FileSystem.joinPaths(str(tmp_path), "a")


def test_join_paths_requires_at_least_one_segment():
    with pytest.raises(BridgeError):
        FileSystem.joinPaths()


def test_json_round_trip(tmp_path, lua):
    path = str(tmp_path / "data.json")
    FileSystem.writeJSON(path, {"a": 1, "b": [1, 2, 3]})
    result = convert.to_py(FileSystem.readJSON(path))
    assert result == {"a": 1, "b": [1, 2, 3]}


def test_read_json_missing_file_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.readJSON(str(tmp_path / "missing.json"))


def test_read_json_malformed_raises_bridge_error(tmp_path):
    path = str(tmp_path / "bad.json")
    FileSystem.writeFile(path, "{not json")
    with pytest.raises(BridgeError):
        FileSystem.readJSON(path)


def test_format_json():
    formatted = FileSystem.formatJSON('{"a":1}', indent=2)
    assert formatted == '{\n  "a": 1\n}'


def test_format_json_malformed_raises_bridge_error():
    with pytest.raises(BridgeError):
        FileSystem.formatJSON("{not json")


def test_read_file_lines(tmp_path, lua):
    path = str(tmp_path / "a.txt")
    FileSystem.writeFile(path, "one\ntwo\nthree")
    assert convert.to_py(FileSystem.readFileLines(path)) == ["one", "two", "three"]


def test_read_file_missing_raises_bridge_error(tmp_path):
    with pytest.raises(BridgeError):
        FileSystem.readFile(str(tmp_path / "missing.txt"))


@pytest.mark.parametrize("path", [None, "", 123])
def test_invalid_path_type_raises_bridge_error(path):
    with pytest.raises(BridgeError):
        FileSystem.readFile(path)
