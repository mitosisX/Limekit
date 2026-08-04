# limekit/toolkit/text.py
"""Safe replacements for the Python builtins P0 stops injecting into Lua."""

import ast
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
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
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
