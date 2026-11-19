"""
factory: new-note
used to create a new note in the vault.

usage:
    uv run .dotfiles/factories/new-note.py TITLE [--description TEXT] [--tags a,b]

TITLE is required and becomes the note title and the file name (slugified),
e.g. "My idea" -> inbox/my-idea.md.

The note is created from .dotfiles/templates/template-note.md. Placeholders
({{title}}, {{date}}, {{description}}, {{tags}}) are filled when present;
otherwise the matching frontmatter fields are filled in place.
"""
# /// script
# requires-python = ">=3.13"
# dependencies = [
# ]
# ///

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# const vars
TEMPLATE_PATH = ".dotfiles/templates/template-note.md"
GENERATE_TARGET = "inbox"

# repo root is two levels above this script (.dotfiles/factories/<script>)
REPO_ROOT = Path(__file__).resolve().parents[2]


def slugify(title: str) -> str:
    """Turn a title into a safe, readable file name."""
    slug = re.sub(r"[^\w\s-]", "", title.strip().lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "untitled"


def fill_frontmatter(content: str, key: str, value: str) -> str:
    """Set an (possibly empty) frontmatter field, e.g. `title:` -> `title: foo`."""
    pattern = rf"^({re.escape(key)}:[ \t]*)(.*)$"
    return re.sub(
        pattern,
        lambda m: f"{m.group(1).rstrip()} {value}".rstrip(),
        content,
        count=1,
        flags=re.MULTILINE,
    )


def render_template(template: str, title: str, description: str, tags: str, note_date: date) -> str:
    """Fill template placeholders and frontmatter fields."""
    values = {
        "title": title,
        "description": description,
        "tags": tags,
        "date": note_date.isoformat(),
    }

    rendered = template
    has_placeholder = False
    for key, value in values.items():
        placeholder = "{{" + key + "}}"
        if placeholder in rendered:
            has_placeholder = True
            rendered = rendered.replace(placeholder, value)

    # templates without placeholders: fill the frontmatter fields directly
    if not has_placeholder:
        if title:
            rendered = fill_frontmatter(rendered, "title", title)
        if description:
            rendered = fill_frontmatter(rendered, "description", description)
        if tags:
            rendered = fill_frontmatter(rendered, "tags", tags)
        rendered = fill_frontmatter(rendered, "created date", note_date.isoformat())
        rendered = fill_frontmatter(rendered, "updated date", note_date.isoformat())

    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a note from the template.",
    )
    parser.add_argument("title", help="title of the note")
    parser.add_argument("--description", default="", help="short description of the note")
    parser.add_argument("--tags", default="", help='comma separated tags, e.g. "idea, reading"')
    args = parser.parse_args()

    title = args.title.strip()
    if not title:
        print("❌ Title must not be empty", file=sys.stderr)
        return 1

    template_path = REPO_ROOT / TEMPLATE_PATH
    target_dir = REPO_ROOT / GENERATE_TARGET
    note_path = target_dir / f"{slugify(title)}.md"

    if note_path.exists():
        print(f"💡 Note already exists, skipped: {note_path.relative_to(REPO_ROOT)}")
        return 0

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}", file=sys.stderr)
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    content = render_template(
        template_path.read_text(encoding="utf-8"),
        title=title,
        description=args.description.strip(),
        tags=args.tags.strip(),
        note_date=date.today(),
    )
    note_path.write_text(content, encoding="utf-8")

    print(f"✅ Created note: {note_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
