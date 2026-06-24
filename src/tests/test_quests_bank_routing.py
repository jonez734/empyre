import ast
import os
import re
from pathlib import Path

import pytest

QUESTS_DIR = Path(__file__).parent.parent / "empyre" / "quests"

PATTERN_COINS_ASSIGN = re.compile(
    r"""player\.coins\s*(?P<op>\+=|-=|=\s*player\.coins\s*[+\-])"""
)

BANK_METHODS = {"add_funds", "remove_funds", "get_balance"}


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
                        if hasattr(node.value.func, 'attr') and node.value.func.attr == 'get_balance':
                            continue
                    lineno = node.lineno
                    self.violations.append(
                        f"Line {lineno}: direct assignment to player.coins"
                    )
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
            self.violations.append(
                f"Line {lineno}: direct augmented assignment to player.coins ({op}=)"
            )
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
        if "player.coins" in line and "bank" not in line.lower():
            if re.search(r"player\.coins\s*[+\-]=", line):
                violations.append(f"Line {i}: direct manipulation of player.coins")

    bank_imported = "bank" in content or "BankService" in content
    has_bank_call = any(method in content for method in BANK_METHODS)

    if "player.coins" in content and not (bank_imported and has_bank_call):
        if not violations:
            violations.append(
                "player.coins used but bank methods not found - may need bank routing"
            )

    return violations


def test_quests_directory_exists():
    assert QUESTS_DIR.exists(), f"Quests directory not found: {QUESTS_DIR}"


def test_all_quest_files_use_bank():
    quest_files = list(QUESTS_DIR.glob("*.py"))
    quest_files = [f for f in quest_files if f.name not in ("__init__.py", "lib.py", "module.py")]

    assert len(quest_files) > 0, "No quest files found"

    all_violations = {}

    for quest_file in quest_files:
        violations = check_file_uses_bank(quest_file)
        if violations:
            all_violations[quest_file.name] = violations

    if all_violations:
        error_msg = "\n\nQuest files with bank routing issues:\n"
        for filename, violations in all_violations.items():
            error_msg += f"\n  {filename}:\n"
            for v in violations:
                error_msg += f"    - {v}\n"
        pytest.fail(error_msg)


def test_raidpiratecamp_uses_bank():
    filepath = QUESTS_DIR / "raidpiratecamp.py"
    if not filepath.exists():
        pytest.skip("raidpiratecamp.py not found")

    violations = check_file_uses_bank(filepath)
    assert not violations, f"raidpiratecamp.py violations:\n" + "\n".join(violations)


def test_zircon_uses_bank():
    filepath = QUESTS_DIR / "zircon.py"
    if not filepath.exists():
        pytest.skip("zircon.py not found")

    violations = check_file_uses_bank(filepath)
    assert not violations, f"zircon.py violations:\n" + "\n".join(violations)


def test_hauntedcave_uses_bank():
    filepath = QUESTS_DIR / "hauntedcave.py"
    if not filepath.exists():
        pytest.skip("hauntedcave.py not found")

    violations = check_file_uses_bank(filepath)
    assert not violations, f"hauntedcave.py violations:\n" + "\n".join(violations)
