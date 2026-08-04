# tests/toolkit/test_text.py
import time

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


def test_power_tower_is_refused_quickly():
    # 9**9**9 is legal arithmetic (only Constant/BinOp/Pow, all permitted
    # node types) but computes 9**387420489 -- a bigint with ~370 million
    # digits. An allowlist over node types cannot reject this; it must be
    # caught by bounding the estimated result size before computing it.
    start = time.monotonic()
    with pytest.raises(BridgeError):
        Sys.evalExpression("9**9**9")
    assert time.monotonic() - start < 1.0, "power tower was not rejected quickly"


def test_deeper_power_tower_is_refused_quickly():
    start = time.monotonic()
    with pytest.raises(BridgeError):
        Sys.evalExpression("9**9**9**2")
    assert time.monotonic() - start < 1.0, "power tower was not rejected quickly"


@pytest.mark.parametrize("expr,expected", [
    ("2**10", 1024),
    ("0**999999", 0),
    ("1**999999", 1),
    ("(-1)**999999", -1),
    ("2**-2", 0.25),
])
def test_legitimate_exponentiation_still_works(expr, expected):
    assert Sys.evalExpression(expr) == expected


def test_power_close_to_the_ceiling_is_not_accidentally_rejected():
    # 2**3000 has about 903 decimal digits -- comfortably under the 1000
    # digit ceiling -- and should evaluate normally, quickly.
    start = time.monotonic()
    result = Sys.evalExpression("2**3000")
    assert time.monotonic() - start < 1.0
    assert result == 2 ** 3000


@pytest.mark.parametrize("expression", [
    {"__lime__": "table"},
    ["1", "+", "1"],
    None,
])
def test_non_string_non_number_input_is_refused(expression):
    with pytest.raises(BridgeError):
        Sys.evalExpression(expression)


@pytest.mark.parametrize("expr", ["1/0", "1//0", "1%0"])
def test_division_by_zero_raises_bridge_error_not_zero_division_error(expr):
    # 1/0 is the single most likely input a real calculator user will type;
    # it must never surface a raw ZeroDivisionError past the bridge.
    with pytest.raises(BridgeError, match="division by zero"):
        Sys.evalExpression(expr)


def test_overflow_raises_bridge_error_not_overflow_error():
    with pytest.raises(BridgeError, match="too large"):
        Sys.evalExpression("1e200**3")


def test_non_finite_result_is_rejected():
    # 1e308 * 10 does not raise OverflowError -- it silently overflows a
    # Python float to +inf. A calculator returning "inf" is not a usable
    # result, so this is rejected the same way an explicit overflow is.
    with pytest.raises(BridgeError, match="not a finite number"):
        Sys.evalExpression("1e308*10")
