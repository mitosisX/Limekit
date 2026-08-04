# limekit/toolkit/text.py
"""Safe replacements for the Python builtins P0 stops injecting into Lua."""

import ast
import math
import operator

from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError

_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

# Ceiling on the estimated decimal-digit length of a ** result. An allowlist
# over node types cannot reject "9**9**9" -- it is legal arithmetic, just
# computationally explosive (9**387420489 has ~370 million digits). We must
# estimate the size of the result *before* computing it and refuse anything
# absurd, rather than let CPython's bigint pow spin forever. 1000 digits
# leaves every realistic calculator use working.
_MAX_POW_DIGITS = 1000


def _check_pow_magnitude(base, exponent):
    """Refuse a ** whose result would be absurdly large, without computing it."""
    if base == 0:
        if exponent < 0:
            raise BridgeError(f"0 ** {exponent!r} is undefined")
        return  # 0**positive == 0, 0**0 == 1: no growth either way
    if abs(base) == 1:
        return  # (+-1)**anything never grows in magnitude
    if exponent == 0:
        return  # anything**0 == 1
    try:
        digits = abs(exponent) * abs(math.log10(abs(base)))
    except (ValueError, OverflowError):
        digits = math.inf
    if digits > _MAX_POW_DIGITS:
        if math.isinf(digits):
            raise BridgeError(f"{base!r} ** {exponent!r} is too large to evaluate safely")
        raise BridgeError(
            f"{base!r} ** {exponent!r} would produce a result with roughly "
            f"{int(digits)} digits; refusing anything over {_MAX_POW_DIGITS} digits"
        )


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant):
        # bool is a subclass of int in Python (isinstance(True, int) is True);
        # exclude it explicitly so True/False don't slip through as 1/0.
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise BridgeError(f"only numbers are allowed, got {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow):
            # Check *before* computing -- computing it to find out how big
            # it is defeats the purpose.
            _check_pow_magnitude(left, right)
        result = _OPERATORS[type(node.op)](left, right)
        if isinstance(result, complex):
            # e.g. (-1)**0.5: legal Python, not a number we can hand back.
            raise BridgeError(f"{left!r} ** {right!r} is not a real number")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise BridgeError(
        f"{type(node).__name__} is not permitted in an expression"
    )


class Sys(LimeObject):
    __lime__ = "sys.Expr"

    @staticmethod
    def evalExpression(expression):
        """Arithmetic only. Never exposes builtins.eval to Lua."""
        if not isinstance(expression, (str, int, float)) or isinstance(expression, bool):
            # A Lua table (or anything else) arriving through the bridge
            # must not be coerced by str() into something that happens to
            # parse -- validate the shape of the input, not just its content.
            raise BridgeError(
                f"expression must be a string or number, got {type(expression).__name__}"
            )
        try:
            tree = ast.parse(str(expression), mode="eval")
        except SyntaxError as exc:
            raise BridgeError(f"malformed expression: {expression!r}") from exc
        except RecursionError as exc:
            # CPython's own parser recurses per nesting level; a pathologically
            # deep expression exhausts it before we ever see a tree to walk.
            raise BridgeError("expression is nested too deeply") from exc
        try:
            return _evaluate(tree)
        except RecursionError as exc:
            raise BridgeError("expression is nested too deeply") from exc
