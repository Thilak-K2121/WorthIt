# ==============================================================================
# Schema Cleanup - Drops Retired (Unused) Columns
# ==============================================================================
# The app manages its schema with Base.metadata.create_all(), which only ever
# ADDS tables. Columns removed from the models therefore linger in PostgreSQL,
# and the NOT NULL ones (whose defaults were Python-side only) would make every
# INSERT fail once the ORM stops sending them. This module drops them.
#
# Idempotent: it inspects the live schema and only drops columns that exist,
# so it is safe to run on every startup and against an already-clean database.
# ==============================================================================

from typing import Dict, List, Tuple

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.core.logging import logger

# table -> columns removed in the 2026-11-17 audit (never displayed, never read by any logic)
RETIRED_COLUMNS: Dict[str, List[str]] = {
    "products": ["verification_status"],
    "product_sources": ["source_title", "source_snippet"],
    "product_discovery_runs": ["candidates_found", "failed_count"],
    "ownerships": [
        "ownership_start_date", "ownership_end_date", "status", "previous_phone",
        "purchase_source", "purchase_country", "owner_session_hash",
    ],
    "experience_reports": ["build_satisfaction", "general_notes"],
    "issue_categories": ["description"],
    "reported_issues": ["severity", "resolved", "repair_cost", "notes"],
    "repair_records": ["covered_under_warranty", "repair_notes"],
    "product_suggestions": ["approximate_release_date", "submitter_ip_hash"],
}


def pending_drops(engine: Engine) -> List[Tuple[str, str]]:
    """Returns (table, column) pairs that still exist in the live database."""
    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    pending = []
    for table, columns in RETIRED_COLUMNS.items():
        if table not in existing_tables:
            continue
        live = {c["name"] for c in insp.get_columns(table)}
        pending.extend((table, col) for col in columns if col in live)
    return pending


def drop_retired_columns(engine: Engine, dry_run: bool = False) -> List[Tuple[str, str]]:
    """Drops every retired column still present. Returns the (table, column) pairs handled."""
    pending = pending_drops(engine)
    if not pending or dry_run:
        return pending

    insp = inspect(engine)
    preparer = engine.dialect.identifier_preparer
    with engine.begin() as conn:  # single transaction: all columns drop, or none do
        for table, column in pending:
            # SQLite refuses to drop an indexed column; PostgreSQL drops the index itself.
            for idx in insp.get_indexes(table):
                if column in (idx.get("column_names") or []):
                    conn.execute(text(f"DROP INDEX IF EXISTS {preparer.quote(idx['name'])}"))
            conn.execute(text(f"ALTER TABLE {preparer.quote(table)} DROP COLUMN {preparer.quote(column)}"))
    logger.info(f"Dropped {len(pending)} retired columns: " + ", ".join(f"{t}.{c}" for t, c in pending))
    return pending
