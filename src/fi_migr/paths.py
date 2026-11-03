"""Polut FI-maahanmuuttopaneelille."""

from __future__ import annotations

from pathlib import Path

from src.config import FIGURES_DIR, ROOT, TABLES_DIR

RAW = ROOT / "data" / "raw" / "national" / "fi_migr"
TABLES = TABLES_DIR / "fi_migr"
FIGURES = FIGURES_DIR / "fi_migr"
DOCS = ROOT / "docs" / "maahanmuutto-fi"
INTERIM = ROOT / "data" / "interim" / "fi_migr"
HAETTU = "2026-11-03"
