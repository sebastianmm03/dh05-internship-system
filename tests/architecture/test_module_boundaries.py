"""T-ARCH-01: the dependency rules of the Module Design are checked, not only written.

ADR-001 says module boundaries are a discipline. These tests read the imports of the
source code and fail when a module reaches into another one in a way the design does
not allow. Routers (api.py) are the composition points that wire modules together.
"""

import ast
from pathlib import Path

from horizon.modules.audit.recorder import AuditRecorder

SRC = Path(__file__).resolve().parents[2] / "src" / "horizon"
MODULES = SRC / "modules"

# Allowed dependencies between implemented modules (Module Design, 'Depends on').
# Everything may use the shared kernel (ports, events), config and infrastructure.
ALLOWED = {
    "placements": {"readiness", "access", "audit"},  # M-03 -> M-04, M-07, M-08
    "readiness": {"rules"},  # M-04 -> M-06
    "rules": set(),  # M-06 is a leaf
    "access": set(),  # M-07 asks nobody: M-03 hands it the relations
    "audit": set(),  # M-08 is a leaf
    "notifications": set(),  # M-09 reacts to events, it imports no module
    "integrations": set(),  # M-11 implements ports, it imports no module
}
FORBIDDEN_IN_PURE_CODE = ("fastapi", "sqlalchemy", "httpx", "requests", "horizon.mocks")
PURE_FILES = [
    MODULES / "placements" / "domain.py",
    MODULES / "rules" / "evaluators.py",
    SRC / "shared" / "ports.py",
]


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
            if node.module == "horizon.modules":  # from horizon.modules import placements
                found += [f"horizon.modules.{alias.name}" for alias in node.names]
    return found


def _module_files(module: str) -> list[Path]:
    return [p for p in (MODULES / module).glob("*.py") if p.name != "api.py"]


def test_modules_only_depend_on_the_modules_the_design_allows() -> None:
    violations = []
    for module, allowed in ALLOWED.items():
        for path in _module_files(module):
            for imported in _imports(path):
                parts = imported.split(".")
                if parts[:2] == ["horizon", "modules"] and len(parts) > 2:
                    target = parts[2]
                    if target != module and target not in allowed:
                        violations.append(f"{path.relative_to(SRC)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_every_implemented_module_is_covered_by_the_rule_table() -> None:
    implemented = {p.name for p in MODULES.iterdir() if p.is_dir() and p.name != "__pycache__"}
    # A planned module (Evaluation 3) is exempt only while it holds nothing but __init__.py;
    # the day it gets real code it needs a row in ALLOWED or this test fails.
    with_code = {
        m for m in implemented if any(p.name != "__init__.py" for p in (MODULES / m).glob("*.py"))
    }
    assert with_code <= set(ALLOWED), f"modules with code but no rule: {with_code - set(ALLOWED)}"


def test_domain_and_rule_code_do_not_import_frameworks_or_adapters() -> None:
    violations = []
    for path in PURE_FILES:
        for imported in _imports(path):
            if imported.startswith(FORBIDDEN_IN_PURE_CODE):
                violations.append(f"{path.relative_to(SRC)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_only_the_integration_module_and_the_composition_points_import_the_mocks() -> None:
    violations = []
    for path in MODULES.rglob("*.py"):
        if path.name == "api.py" or path.parent.name == "integrations":
            continue
        for imported in _imports(path):
            if imported.startswith("horizon.mocks"):
                violations.append(f"{path.relative_to(SRC)} imports {imported}")
    assert not violations, "\n".join(violations)


def test_audit_history_can_only_be_appended_and_read() -> None:
    public = {name for name in dir(AuditRecorder) if not name.startswith("_")}
    assert public == {"record", "history"}  # ADR-006: no update, no delete
