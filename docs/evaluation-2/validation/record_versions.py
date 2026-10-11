"""Write versions.txt with the versions used to run the evidence on this computer.

usage: python docs/evaluation-2/validation/record_versions.py
"""

import platform
import sqlite3
import sys
from importlib.metadata import version
from pathlib import Path

lines = [f"python {platform.python_version()} {platform.platform()}"]
for pkg in ("fastapi", "sqlalchemy", "pytest", "ruff", "pydantic", "httpx"):
    lines.append(f"{pkg} {version(pkg)}")
lines.append(f"sqlite {sqlite3.sqlite_version}")
out = Path(__file__).with_name("versions.txt")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
sys.exit(0)
