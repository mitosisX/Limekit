"""The channel between a launcher and a project it started.

1.x's code injection wrote Lua to a file and hoped. That cannot report a
result, cannot report an error, cannot say what the running application
contains, and 2.0 never read the file at all -- so the feature has been
inert for the whole of this version's life.

This replaces it with a socket. QLocalSocket is a named pipe on Windows and
a unix socket elsewhere, it is event-driven rather than polled, and it goes
both ways -- which is the part that matters, because the useful direction is
the app answering questions about itself.

    launcher                          project
    --------                          -------
    InspectorServer.listen()   ->  LIMEKIT_INSPECT=<name> in the environment
                               <-  connects on boot
    {"id":1,"op":"tree"}       ->
                               <-  {"id":1,"ok":true,"result":[...]}

One line of JSON per message, UTF-8, newline-terminated.

Off unless asked for. 2.0 deliberately closed lupa's `python.*` table, and
nothing here reopens it: the channel runs Lua in the project's own runtime,
reads properties the registry already declares, and exists only when a
launcher put LIMEKIT_INSPECT in the environment. A project cannot switch it
on for itself.
"""

import json
import os

from PySide6.QtCore import QObject
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.services import inspect as inspection

ENV_VAR = "LIMEKIT_INSPECT"

# Qt gives no framing of its own -- a socket read may hold half a message or
# three, so every message is one line and the reader buffers until it has
# one. Newline is safe because the payload is JSON, which escapes its own.
_TERMINATOR = b"\n"


def _encode(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8") + _TERMINATOR


class _LineReader:
    """Reassembles newline-terminated messages from arbitrary reads."""

    def __init__(self):
        self._buffer = bytearray()

    def feed(self, chunk):
        self._buffer.extend(chunk)
        while True:
            index = self._buffer.find(_TERMINATOR)
            if index < 0:
                return
            line = bytes(self._buffer[:index])
            del self._buffer[:index + 1]
            if not line.strip():
                continue
            try:
                yield json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue                      # a malformed line, not a crash


class ProjectInspector(QObject):
    """The project's end. Answers questions about itself.

    Started by the launcher's environment, never by the project's own Lua.
    """

    def __init__(self, server_name, runtime, parent=None):
        super().__init__(parent)
        self._runtime = runtime
        self._reader = _LineReader()
        self._socket = QLocalSocket(self)
        self._socket.readyRead.connect(self._onReadyRead)
        self._socket.connectToServer(server_name)

    def isConnected(self):
        return self._socket.state() == QLocalSocket.LocalSocketState.ConnectedState

    def close(self):
        self._socket.disconnectFromServer()

    # -- wire --------------------------------------------------------------

    def _onReadyRead(self):
        for message in self._reader.feed(bytes(self._socket.readAll())):
            self._socket.write(_encode(self.handle(message)))
        self._socket.flush()

    def handle(self, message):
        """One request in, one reply out. Never raises.

        A failure here is the far end's answer, not this process's problem:
        the app being inspected must not die because a launcher asked it
        something it could not do.
        """
        reply = {"id": message.get("id")}
        try:
            reply["result"] = self.dispatch(message)
            reply["ok"] = True
        except Exception as exc:
            reply["ok"] = False
            # The message alone: "ValueError: ..." names a Python class the
            # person reading it never wrote.
            reply["error"] = str(exc) or "it failed, without saying why"
        return reply

    # -- operations --------------------------------------------------------

    def dispatch(self, message):
        op = message.get("op")
        handler = getattr(self, f"_op_{op}", None) if isinstance(op, str) else None
        if handler is None:
            raise BridgeError(f"unknown operation {op!r}")
        return handler(message)

    @staticmethod
    def _op_ping(_message):
        return "pong"

    @staticmethod
    def _op_tree(message):
        return inspection.tree(max_depth=int(message.get("depth", 12)))

    @staticmethod
    def _widget(message):
        path = message.get("path")
        widget = inspection.resolve(path)
        if widget is None:
            raise BridgeError(f"nothing at path {path!r} -- the tree may be stale")
        return widget

    @classmethod
    def _op_props(cls, message):
        widget = cls._widget(message)
        return {
            "path": message.get("path"),
            "class": inspection.lime_name(widget),
            "props": inspection.properties(widget),
        }

    @classmethod
    def _op_set(cls, message):
        widget = cls._widget(message)
        name = message.get("prop")
        return {"name": name,
                "value": inspection.set_property(widget, name, message.get("value"))}

    def _op_eval(self, message):
        """Run Lua in the project's own runtime.

        The chunk is named so a mistake in it reports as coming from the
        injector rather than from the author's own file.
        """
        code = message.get("code") or ""
        if not code.strip():
            raise BridgeError("nothing to run")

        result = self._runtime.execute(code, chunkname="<injected>")
        if result is None:
            return ""
        if isinstance(result, bool):
            return "true" if result else "false"
        if isinstance(result, (str, int, float)):
            return str(result)
        return inspection.describe(result)


def start_if_requested(runtime):
    """Connect back to a launcher, if one asked for it.

    Returns the inspector so the caller can hold it: a QObject with no parent
    and no reference is collected, and takes the socket with it.
    """
    name = os.environ.get(ENV_VAR)
    if not name:
        return None
    return ProjectInspector(name, runtime)


class Inspector(LimeObject, QObject):
    """The launcher's end, exposed to Lua as `sys.Inspector`.

    Limer stands one of these up, puts its name in the child's environment,
    and asks the running project questions once it connects.
    """

    __lime__ = "sys.Inspector"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._onNewConnection)
        self._socket = None
        self._reader = _LineReader()
        self._pending = {}
        self._nextId = 1
        self._onConnect = None
        self._onDisconnect = None

    @method(returns="string",
            doc="Starts listening and returns the name to give the project. "
                "Safe to call again: an open channel keeps its name.")
    def listen(self):
        """Open the channel, or hand back the one already open.

        A launcher asks for this every time it starts a project, and a
        QLocalServer that is already listening refuses to listen again --
        so a first version of this worked once per session and then failed
        silently on every subsequent run. Being idempotent is not a
        convenience here; the obvious caller cannot work without it.
        """
        if self._server.isListening():
            return self._server.serverName()

        # A previous run that died without closing leaves the name taken on
        # unix; Qt will not reuse it until it is removed.
        name = f"limekit-inspect-{os.getpid()}-{id(self) & 0xffff:x}"
        QLocalServer.removeServer(name)
        if not self._server.listen(name):
            raise BridgeError(
                f"could not listen on {name!r}: {self._server.errorString()}"
            )
        return self._server.serverName()

    @method(returns="string", doc="The name being listened on, or an empty string.")
    def getName(self):
        return self._server.serverName()

    @method(returns="boolean", doc="Whether a project is currently connected.")
    def isConnected(self):
        return (self._socket is not None
                and self._socket.state() == QLocalSocket.LocalSocketState.ConnectedState)

    @method(doc="Stops listening and drops any connected project.")
    def close(self):
        if self._socket is not None:
            self._socket.disconnectFromServer()
            self._socket = None
        self._server.close()
        self._pending.clear()
        return True

    # -- events ------------------------------------------------------------

    @method({"handler": "fun()"}, returns="self",
            doc="Called when the running project connects back.")
    def setOnConnect(self, handler):
        from limekit.kernel.bridge.guard import guard
        self._onConnect = guard(handler, widget="Inspector", event="onConnect")
        return self

    @method({"handler": "fun()"}, returns="self",
            doc="Called when the running project goes away.")
    def setOnDisconnect(self, handler):
        from limekit.kernel.bridge.guard import guard
        self._onDisconnect = guard(handler, widget="Inspector", event="onDisconnect")
        return self

    # -- requests ----------------------------------------------------------

    @method({"op": "string", "args": "table", "handler": "fun(ok: boolean, result: any)"},
            returns="boolean",
            doc="Asks the running project something. The handler receives (ok, result).")
    def request(self, op, args=None, handler=None):
        """Send one request. The reply arrives on `handler`, later.

        Returns false rather than raising when nothing is connected: a
        launcher asking a project that has just exited is ordinary, and it
        already has to handle the not-connected case anyway.
        """
        if not self.isConnected():
            return False

        from limekit.kernel.bridge.convert import as_mapping
        from limekit.kernel.bridge.guard import guard

        message = {"op": str(op)}
        if args is not None:
            message.update(as_mapping(args))

        message["id"] = self._nextId
        self._nextId += 1

        if handler is not None:
            self._pending[message["id"]] = guard(
                handler, widget="Inspector", event="request"
            )

        self._socket.write(_encode(message))
        self._socket.flush()
        return True

    # -- wire --------------------------------------------------------------

    def _onNewConnection(self):
        socket = self._server.nextPendingConnection()
        if socket is None:
            return

        # One project at a time: a second connection would answer questions
        # asked of the first, and Limer only ever runs one.
        if self._socket is not None:
            socket.disconnectFromServer()
            return

        self._socket = socket
        self._reader = _LineReader()
        socket.readyRead.connect(self._onReadyRead)
        socket.disconnected.connect(self._onDisconnected)

        if self._onConnect is not None:
            self._onConnect()

    def _onDisconnected(self):
        self._socket = None
        self._pending.clear()
        if self._onDisconnect is not None:
            self._onDisconnect()

    def _onReadyRead(self):
        from limekit.kernel.bridge.convert import to_lua

        for message in self._reader.feed(bytes(self._socket.readAll())):
            handler = self._pending.pop(message.get("id"), None)
            if handler is None:
                continue
            ok = bool(message.get("ok"))
            payload = message.get("result") if ok else message.get("error", "")
            handler(ok, to_lua(payload))
