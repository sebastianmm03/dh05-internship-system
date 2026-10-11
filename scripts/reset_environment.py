import argparse
from pathlib import Path

from horizon.config import get_settings
from horizon.infrastructure.database import Base, engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reset the Horizon starter environment.")
    parser.add_argument(
        "--drop-schema",
        action="store_true",
        help="Drop all starter database tables.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()

    if args.drop_schema:
        Base.metadata.drop_all(bind=engine)
        print("Starter database schema dropped.")

    generated = settings.data_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    for path in generated.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_file():
            path.unlink()
    print("Generated reports removed.")

    if settings.database_url.startswith("sqlite:///./"):
        database_file = Path(settings.database_url.removeprefix("sqlite:///./"))
        if database_file.exists():
            database_file.unlink()
            print(f"SQLite database removed: {database_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
