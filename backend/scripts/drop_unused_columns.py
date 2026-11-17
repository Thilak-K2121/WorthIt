"""
Preview or apply the removal of unused database columns.

  python scripts/drop_unused_columns.py            # dry run: lists what would be dropped
  python scripts/drop_unused_columns.py --apply    # drops them (irreversible: back up first)

Uses DATABASE_URL from the environment / backend/.env. The same cleanup also runs
automatically on app startup, so running this by hand is optional.
"""

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.core.database import engine  # noqa: E402
from app.core.schema_cleanup import drop_retired_columns  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually drop the columns")
    args = ap.parse_args()

    print(f"Database: {engine.url.render_as_string(hide_password=True)}")
    handled = drop_retired_columns(engine, dry_run=not args.apply)
    if not handled:
        print("Nothing to drop: schema is already clean.")
        return
    verb = "Dropped" if args.apply else "Would drop"
    for table, column in handled:
        print(f"  {verb} {table}.{column}")
    if not args.apply:
        print("\nDry run only. Re-run with --apply to drop them.")


if __name__ == "__main__":
    main()
