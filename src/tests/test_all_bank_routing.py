import ast
import re
from pathlib import Path

import pytest

EMPYRE_SRC = Path(__file__).parent.parent / "empyre"

EXCLUDE_DIRS = {"__pycache__", "data", "sql", ".pytest_cache"}
EXCLUDE_FILES = {"__init__.py", "player.py", "lib.py", "_version.py", "testsuper.py"}


def get_all_python_files(src_dir: Path) -> list[Path]:
    files = []
    for item in src_dir.rglob("*.py"):
        rel_parts = set(item.relative_to(src_dir).parts)
        if any(excl in rel_parts for excl in EXCLUDE_DIRS):
            continue
        if item.name in EXCLUDE_FILES:
            continue
        files.append(item)
    return files


class CoinsAssignmentVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if (
                    isinstance(target.value, ast.Name)
                    and target.value.id == "player"
                    and target.attr == "coins"
                ):
                    if isinstance(node.value, ast.Call):
                        if hasattr(node.value.func, "attr") and node.value.func.attr == "get_balance":
                            continue
                    lineno = node.lineno
                    self.violations.append(f"Line {lineno}: direct assignment to player.coins")
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if (
            isinstance(node.target, ast.Attribute)
            and isinstance(node.target.value, ast.Name)
            and node.target.value.id == "player"
            and node.target.attr == "coins"
        ):
            lineno = node.lineno
            op = ast.unparse(node.op)
            self.violations.append(f"Line {lineno}: direct augmented assignment to player.coins ({op}=)")
        self.generic_visit(node)


def check_file_uses_bank(filepath: Path) -> list[str]:
    content = filepath.read_text()
    violations = []

    try:
        tree = ast.parse(content, filename=str(filepath))
        visitor = CoinsAssignmentVisitor()
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:
        violations.append(f"Syntax error: {e}")

    for i, line in enumerate(content.splitlines(), 1):
        if re.search(r"player\.coins\s*[+\-]=", line):
            violations.append(f"Line {i}: direct manipulation of player.coins")

    return violations


def test_all_empyre_modules_checked():
    all_files = get_all_python_files(EMPYRE_SRC)
    assert len(all_files) > 0, "No Python files found in empyre source"

    modules_with_violations = {}
    modules_with_coins = {}

    for filepath in all_files:
        content = filepath.read_text()

        if "player.coins" not in content:
            continue

        modules_with_coins[str(filepath.relative_to(EMPYRE_SRC))] = True
        violations = check_file_uses_bank(filepath)

        if violations:
            modules_with_violations[str(filepath.relative_to(EMPYRE_SRC))] = violations

    if modules_with_violations:
        error_msg = "\n\nEmpyre modules with direct coin manipulation:\n"
        for filename, violations in modules_with_violations.items():
            error_msg += f"\n  {filename}:\n"
            for v in violations:
                error_msg += f"    - {v}\n"
        error_msg += f"\n\nTotal modules with player.coins: {len(modules_with_coins)}"
        error_msg += f"\nTotal modules with violations: {len(modules_with_violations)}"
        pytest.fail(error_msg)
