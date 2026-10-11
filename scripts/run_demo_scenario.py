import argparse
import json
from pathlib import Path

from horizon.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Display a synthetic project scenario.")
    parser.add_argument(
        "scenario",
        nargs="?",
        default="sample_scenario.json",
        help="Scenario filename under data/scenarios.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = get_settings().data_root / "scenarios" / Path(args.scenario).name
    if not path.exists():
        print(f"Scenario not found: {path}")
        return 1

    scenario = json.loads(path.read_text(encoding="utf-8"))
    print(f"{scenario['scenario_id']} — {scenario['title']}")
    print("\nKnown conditions:")
    for condition in scenario.get("known_conditions", []):
        print(f"- {condition}")
    print("\nDesign questions:")
    for question in scenario.get("questions", []):
        print(f"- {question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
