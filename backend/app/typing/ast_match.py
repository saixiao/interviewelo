"""Structural (AST-level) comparison of a single line of Python code.

Used by Reaction mode: the user reads a line, it stays visible while they type
it, and on submit we need to judge whether they reproduced its *logical
syntax* rather than its exact characters. Concretely: variable/parameter/def
names and literal values are incidental (renaming `nums` to `arr`, or typing
`5` instead of `3`, shouldn't fail the line) but keywords, operators, control
flow shape, and which functions/attributes are called must match.

Lines are wrapped in a dummy function before parsing so statements that are
only valid inside a function body (`return`, `yield`) or that open a block
(`for ...:`, `if ...:`) parse in isolation. When a line still can't be parsed
(e.g. a bare `else:`), we fall back to whitespace-normalized text equality
rather than raising.
"""

import ast

_WRAPPER_HEADER = "def __wrapper__():\n    "


def _parse_statement(line: str) -> ast.stmt:
    stripped = line.strip()
    if not stripped:
        raise SyntaxError("empty line")

    for candidate in (stripped, f"{stripped}\n    pass"):
        indented = candidate.replace("\n", "\n    ")
        try:
            module = ast.parse(_WRAPPER_HEADER + indented)
        except SyntaxError:
            continue
        wrapper_fn = module.body[0]
        assert isinstance(wrapper_fn, ast.FunctionDef)
        return wrapper_fn.body[0]

    raise SyntaxError(f"could not parse line: {line!r}")


_NAME_AGNOSTIC_NODE_FIELDS = {
    (ast.Name, "id"),
    (ast.arg, "arg"),
    (ast.FunctionDef, "name"),
    (ast.AsyncFunctionDef, "name"),
    (ast.ClassDef, "name"),
}


def _signature(node: object) -> object:
    """A hashable value capturing a node's structural shape while erasing
    incidental identifier names and literal values (see module docstring)."""
    if isinstance(node, ast.AST):
        parts: list[object] = [type(node).__name__]
        for field_name, value in ast.iter_fields(node):
            if field_name == "ctx":
                continue  # Load/Store/Del is noise, not a syntax choice

            # Which function is being called is not incidental, even though
            # its AST node is a plain Name like any other variable reference.
            if isinstance(node, ast.Call) and field_name == "func" and isinstance(value, ast.Name):
                parts.append(("Name", value.id))
                continue

            if (type(node), field_name) in _NAME_AGNOSTIC_NODE_FIELDS:
                parts.append("*")
                continue

            if isinstance(node, ast.Constant) and field_name == "value":
                parts.append(type(value).__name__)
                continue

            parts.append(_signature(value))
        return tuple(parts)

    if isinstance(node, list):
        return tuple(_signature(item) for item in node)

    return node


def _normalized_text(line: str) -> str:
    return " ".join(line.split())


def lines_match(target: str, typed: str) -> bool:
    """Whether `typed` reproduces the logical syntax of `target`."""
    if not target.strip() and not typed.strip():
        return True

    try:
        target_ast = _parse_statement(target)
        typed_ast = _parse_statement(typed)
    except SyntaxError:
        return _normalized_text(target) == _normalized_text(typed)

    return _signature(target_ast) == _signature(typed_ast)
