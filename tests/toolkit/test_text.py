# tests/toolkit/test_text.py
import pytest
from limekit.toolkit.text import Sys
from limekit.kernel.errors import BridgeError


@pytest.mark.parametrize("expr,expected", [
    ("1 + 1", 2), ("2 * (3 + 4)", 14), ("-5 + 2", -3), ("7 / 2", 3.5),
])
def test_arithmetic(expr, expected):
    assert Sys.evalExpression(expr) == expected


@pytest.mark.parametrize("expr", [
    "__import__('os').system('echo pwned')",
    "open('/etc/passwd').read()",
    "[].__class__",
    "lambda: 1",
])
def test_code_execution_is_refused(expr):
    with pytest.raises(BridgeError):
        Sys.evalExpression(expr)


def test_malformed_expression_raises():
    with pytest.raises(BridgeError, match="malformed"):
        Sys.evalExpression("1 +")
