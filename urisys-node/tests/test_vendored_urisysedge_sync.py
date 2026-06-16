"""Guard the intentionally-vendored `urisysedge` copy against functional drift.

urisys-node ships its own copy of `urisysedge` (runtime/env) so it can be
`pip install`ed standalone, without depending on the full `urisys` package
(see urisysedge/__init__.py docstring). That is deliberate — but the two copies
must stay functionally identical. This test fails if their *code* diverges
(comments and docstrings are allowed to differ for context).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

NODE_EDGE = Path(__file__).resolve().parents[1] / "packages" / "python" / "urisysedge"
CANONICAL_EDGE = Path(__file__).resolve().parents[2] / "packages" / "python" / "urisysedge"

# Modules that carry behaviour and must not drift. __init__.py is excluded:
# its docstring intentionally describes the bundling context.
GUARDED_MODULES = ["runtime.py", "env.py"]


def _normalized_code(path: Path) -> str:
    """Source with comments, docstrings and formatting removed, so only the
    functional structure is compared (ast.unparse drops comments entirely)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    # Strip module/class/function docstrings (allowed to differ for context).
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return ast.unparse(ast.parse(ast.unparse(tree)))


@pytest.mark.parametrize("module", GUARDED_MODULES)
def test_vendored_urisysedge_matches_canonical(module: str):
    vendored = NODE_EDGE / module
    canonical = CANONICAL_EDGE / module
    if not canonical.is_file():
        pytest.skip(f"canonical urisysedge not present at {canonical} (standalone checkout)")
    assert vendored.is_file(), f"vendored copy missing: {vendored}"
    assert _normalized_code(vendored) == _normalized_code(canonical), (
        f"urisysedge/{module} drifted from canonical "
        f"({CANONICAL_EDGE}). Re-sync the vendored copy in urisys-node "
        f"(only comments/docstrings may differ)."
    )
