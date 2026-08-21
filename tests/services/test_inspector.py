"""The launcher/project channel: framing, dispatch, and failure behaviour."""

import json

import pytest
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest
from limekit.services import inspector


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


# -- framing ---------------------------------------------------------------

def test_a_message_split_across_reads_is_reassembled():
    """Qt hands over bytes, not messages. Half a line is normal."""
    reader = inspector._LineReader()
    assert list(reader.feed(b'{"op":"pi')) == []
    assert list(reader.feed(b'ng"}\n')) == [{"op": "ping"}]


def test_several_messages_in_one_read_all_come_out():
    reader = inspector._LineReader()
    assert list(reader.feed(b'{"a":1}\n{"a":2}\n')) == [{"a": 1}, {"a": 2}]


def test_a_malformed_line_is_skipped_rather_than_fatal():
    """A launcher writing rubbish must not take the inspected app down."""
    reader = inspector._LineReader()
    assert list(reader.feed(b'not json\n{"a":1}\n')) == [{"a": 1}]


def test_encoding_terminates_every_message():
    assert inspector._encode({"a": 1}).endswith(b"\n")
    assert json.loads(inspector._encode({"a": 1})) == {"a": 1}


# -- dispatch --------------------------------------------------------------

class _FakeRuntime:
    def __init__(self):
        self.ran = []

    def execute(self, source, chunkname=None):
        self.ran.append((source, chunkname))
        if "boom" in source:
            raise ValueError("boom")
        return None


@pytest.fixture
def project_end(qapp):
    """A ProjectInspector with no socket, driven straight through handle()."""
    end = inspector.ProjectInspector.__new__(inspector.ProjectInspector)
    end._runtime = _FakeRuntime()
    return end


def test_ping_answers(project_end):
    assert project_end.handle({"id": 7, "op": "ping"}) == {
        "id": 7, "ok": True, "result": "pong",
    }


def test_an_unknown_operation_is_an_error_not_an_exception(project_end):
    reply = project_end.handle({"id": 1, "op": "nonsense"})
    assert reply["ok"] is False
    assert "nonsense" in reply["error"]


def test_a_failing_operation_never_escapes_handle(project_end):
    """The app being inspected must not die because a launcher asked badly."""
    reply = project_end.handle({"id": 1, "op": "props", "path": "9.9.9"})
    assert reply["ok"] is False
    assert "9.9.9" in reply["error"]


def test_eval_runs_in_the_projects_own_runtime(project_end):
    reply = project_end.handle({"id": 1, "op": "eval", "code": "x = 1"})
    assert reply["ok"] is True
    assert project_end._runtime.ran == [("x = 1", "<injected>")]


def test_eval_names_its_chunk_so_a_mistake_is_not_blamed_on_the_author(project_end):
    project_end.handle({"id": 1, "op": "eval", "code": "boom"})
    assert project_end._runtime.ran[-1][1] == "<injected>"


def test_eval_rejects_an_empty_chunk(project_end):
    reply = project_end.handle({"id": 1, "op": "eval", "code": "   "})
    assert reply["ok"] is False
    assert "nothing to run" in reply["error"]


def test_a_failing_chunk_reports_rather_than_propagates(project_end):
    reply = project_end.handle({"id": 1, "op": "eval", "code": "boom"})
    assert reply["ok"] is False
    assert "boom" in reply["error"]


# -- the launcher end ------------------------------------------------------

def test_the_channel_is_off_unless_a_launcher_asked_for_it(monkeypatch):
    """2.0 closed python.*; nothing here may reopen it by default."""
    monkeypatch.delenv(inspector.ENV_VAR, raising=False)
    assert inspector.start_if_requested(_FakeRuntime()) is None


def test_a_request_with_nobody_connected_is_refused_not_raised(qapp):
    server = inspector.Inspector()
    assert server.isConnected() is False
    assert server.request("tree") is False
    server.close()


def test_listen_returns_the_name_to_hand_the_project(qapp):
    server = inspector.Inspector()
    name = server.listen()
    assert name and server.getName() == name
    server.close()


def test_listen_can_be_called_again_and_keeps_its_name(qapp):
    """The obvious caller asks on every run, and cannot work otherwise.

    A QLocalServer that is already listening refuses to listen again, so a
    version of this that was not idempotent opened the channel for the first
    project of a session and then failed silently for every one after it.
    """
    server = inspector.Inspector()
    first = server.listen()
    assert server.listen() == first
    assert server.listen() == first
    server.close()


def test_a_closed_channel_can_be_opened_again(qapp):
    server = inspector.Inspector()
    server.listen()
    server.close()
    assert server.listen()
    server.close()
