"""
factory: new-daily-note
used to create a new daily note in the vault.

usage:
    uv run .dotfiles/factories/new-daily.py [DATE]

DATE defaults to the date of running time and accepts:
    - today / yesterday / tomorrow
    - YYYY-MM-DD (e.g. 2025-01-31)
    - YYYY/MM/DD, YYYY.MM.DD
    - MM-DD / MM/DD (current year)
"""
# /// script
# requires-python = ">=3.13"
# dependencies = [
# ]
# ///

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

# const vars
TEMPLATE_PATH = ".dotfiles/templates/template-daily.md"
GENERATE_TARGET = "daily-notes"

# repo root is two levels above this script (.dotfiles/factories/<script>)
REPO_ROOT = Path(__file__).resolve().parents[2]

RELATIVE_DATES = {
    "today": 0,
    "yesterday": -1,
    "tomorrow": 1,
}


def parse_date(value: str) -> date:
    """Parse a date argument into a date object."""
    key = value.strip().lower()
    if key in RELATIVE_DATES:
        return date.today() + timedelta(days=RELATIVE_DATES[key])

    normalized = key.replace("/", "-").replace(".", "-")
    parts = normalized.split("-")

    # current-year shorthand: MM-DD
    if len(parts) == 2:
        normalized = f"{date.today().year}-{normalized}"

    try:
        return date.fromisoformat(normalized)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date: {value!r} (expected e.g. 2025-01-31, today, yesterday, tomorrow)"
        )


def render_template(template: str, note_date: date) -> str:
    """Fill template placeholders."""
    values = {
        "date": note_date.isoformat(),
        "year": f"{note_date.year:04d}",
        "month": f"{note_date.month:02d}",
        "day": f"{note_date.day:02d}",
        "weekday": note_date.strftime("%A"),
    }
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a daily note from the template.",
    )
    parser.add_argument(
        "date",
        nargs="?",
        default=None,
        type=parse_date,
        help="date of the note (default: date of running time)",
    )
    args = parser.parse_args()

    note_date: date = args.date or date.today()
    template_path = REPO_ROOT / TEMPLATE_PATH
    target_dir = REPO_ROOT / GENERATE_TARGET
    note_path = target_dir / f"{note_date.isoformat()}.md"

    if note_path.exists():
        print(f"💡 Daily note already exists, skipped: {note_path.relative_to(REPO_ROOT)}")
        return 0

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}", file=sys.stderr)
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    content = render_template(template_path.read_text(encoding="utf-8"), note_date)
    note_path.write_text(content, encoding="utf-8")

    print(f"✅ Created daily note: {note_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
