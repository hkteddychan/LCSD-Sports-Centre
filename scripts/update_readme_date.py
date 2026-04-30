#!/usr/bin/env python3
"""
Update the 'Last Updated' badge date in README.md to today's date.
Run after fetch_venue_data.py when the GeoJSON was actually updated.
"""
import re
from datetime import datetime
from pathlib import Path

README_PATH = Path(__file__).parent.parent / "README.md"


def update_readme_date():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Updating README badge date to: {today}")

    content = README_PATH.read_text(encoding="utf-8")

    # Replace the Last Updated badge date
    # Badge format: [![Last Updated](https://img.shields.io/badge/Last%20Updated-YYYY--MM--DD-orange)]
    updated = re.sub(
        r'(\!\[Last Updated\]\([^)]+Last%20Updated-)[^)]+(-orange\))',
        rf'\g<1>{today.replace("-", "--")}\g<2>',
        content
    )

    # Also update the inline text date in spec/spec section if present
    # Pattern: Last Updated: 2026-04-28
    updated = re.sub(
        r'(Last Updated: )\d{4}-\d{2}-\d{2}',
        rf'\g<1>{today}',
        updated
    )

    if updated != content:
        README_PATH.write_text(updated, encoding="utf-8")
        print("  → README.md updated")
    else:
        print("  → No badge found or date unchanged, nothing to do")


if __name__ == "__main__":
    update_readme_date()
