#!/usr/bin/env python3
"""
Bulk GlobAllomeTree importer (staging step).

Purpose:
- Take a raw GlobAllomeTree export (CSV/TSV)
- Load it safely (no assumptions yet)
- Emit a staging CSV into data/staging/ for subsequent normalization/validation steps
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_DIR = REPO_ROOT / "data" / "staging"


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in [".tsv", ".tab"]:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage a raw GlobAllomeTree table for import.")
    parser.add_argument("input", type=str, help="Path to raw GlobAllomeTree export (CSV/TSV).")
    parser.add_argument("--out", type=str, default="", help="Optional explicit output path.")
    args = parser.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    df = read_table(in_path)

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out).expanduser().resolve() if args.out else (STAGING_DIR / f"{in_path.stem}__staged.csv")

    print("=== GlobAllomeTree Import: STAGE ===")
    print(f"Input:  {in_path}")
    print(f"Rows:   {len(df):,}")
    print(f"Cols:   {len(df.columns):,}")
    print("Columns:")
    for c in df.columns:
        print(f" - {c}")

    df.to_csv(out_path, index=False)
    print(f"\nWrote staging file: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
