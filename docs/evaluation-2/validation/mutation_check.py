"""Hand-written mutation check: inject a defect, run the suite on a COPY, expect a failure.

usage: python mutation_check.py <repository root> [python with pytest]
(by default the same Python that runs this script, so an active virtual environment is used)
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
ROOT = Path(sys.argv[1]).resolve()
PY = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "python" else sys.executable
MUTATIONS = [
    (
        "M1 remove the conditional update (compare-and-set)",
        "src/horizon/modules/placements/repository.py",
        "                PlacementModel.status == expected_status.value,\n",
        "",
    ),
    (
        "M2 directory failure lets the gate pass (fail open)",
        "src/horizon/modules/rules/evaluators.py",
        'except ExternalServiceUnavailable as error:\n            return [Blocking("VALID_AGREEMENT", None, f"agreement could not be verified ({error})")]',
        "except ExternalServiceUnavailable:\n            return []",
    ),
    (
        "M3 projection stops hiding restricted evidence",
        "src/horizon/modules/access/policy.py",
        'visible["evidence_reference"] = None',
        "pass",
    ),
    (
        "M4 student may activate",
        "src/horizon/modules/access/policy.py",
        '"placement.activate": {"office"}\n            if actor.staff_role == "EXPERIENTIAL_LEARNING_COORDINATOR"\n            else set(),',
        '"placement.activate": {"office", "student"},',
    ),
    (
        "M5 rules module imports placements (boundary violation)",
        "src/horizon/modules/rules/evaluators.py",
        "import json\n",
        "import json\nimport horizon.modules.placements.domain  # noqa\n",
    ),
    (
        "M6 worker commits once at the end again",
        "src/horizon/modules/notifications/outbox.py",
        "        session.commit()  # one commit per message: a crash never repeats an already sent one\n    return summary",
        "    session.commit()\n    return summary",
    ),
]


def run_suite(work):
    r = subprocess.run(
        [PY, "-m", "pytest", "-o", "addopts=", "-q", "-x", "-p", "no:cacheprovider"],
        check=False,
        cwd=work,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": str(work / "src"), "PYTHONIOENCODING": "utf-8"},
    )
    text = (r.stdout + r.stderr).replace(str(work), "<copy>").replace(str(ROOT), "<repo>")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    hits = [line for line in lines if line.startswith("FAILED ")]
    hits += [line for line in lines if "AssertionError" in line or "passed" in line or "rror" in line]
    return r.returncode, (hits[0] if hits else (lines[-1] if lines else ""))[:150]


def imported_from(work):
    """Where the copy really imports the application from (must be the copy, not the repository)."""
    r = subprocess.run(
        [PY, "-c", "import horizon; print(horizon.__file__)"],
        check=False,
        cwd=work,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": str(work / "src"), "PYTHONIOENCODING": "utf-8"},
    )
    out = r.stdout.strip()
    norm = os.path.normcase(os.path.realpath(out)) if out else ""
    inside = norm.startswith(os.path.normcase(os.path.realpath(work)))
    return "<copy>" if inside else (out or r.stderr.strip()[-150:])


def fresh_copy():
    work = Path(tempfile.mkdtemp()) / "mut_run"  # outside the repository
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".venv", ".git", "*.egg-info"))
    return work


# Baseline: the unmodified copy must pass, otherwise a failure would not mean "detected".
work = fresh_copy()
source = imported_from(work)
code, detail = run_suite(work)
shutil.rmtree(work.parent, ignore_errors=True)
print(f"BASELINE (no defect): {'PASSED' if code == 0 else 'FAILED'} -> {detail}")
print(f"Application imported from: {source}")
if code != 0 or source != "<copy>":
    sys.exit(1)

for name, rel, old, new in MUTATIONS:
    work = fresh_copy()
    f = work / rel
    text = f.read_text(encoding="utf-8")
    if old not in text:
        print(f"{name}: PATTERN NOT FOUND")
        shutil.rmtree(work.parent, ignore_errors=True)
        continue
    f.write_text(text.replace(old, new, 1), encoding="utf-8")
    code, detail = run_suite(work)
    verdict = "DETECTED" if code else "NOT DETECTED"
    print(f"{name}: {verdict} -> {detail}")
    shutil.rmtree(work.parent, ignore_errors=True)
