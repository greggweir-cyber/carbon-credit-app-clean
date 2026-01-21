#!/usr/bin/env python3
"""
Normalize a staged GlobAllomeTree table into the app-ready raw import schema.

Input (current example): species_name, region, component, equation_type, formula_text, wood_density
Output: globallometree_raw_import.csv-compatible columns (superset)

This is an incremental normalizer:
- Step 2: map what we have + leave the rest blank
- Step 3: add parsing for predictor vars (DBH/Height), units, bounds, sources, etc.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

RAW_IMPORT_COLUMNS = [
    "species_name",
    "region",
    "component",
    "equation_type",
    "predictor_vars",
    "formula_text",
    "biomass_units",
    "dbh_units",
    "dbh_min",
    "dbh_max",
    "height_units",
    "height_min",
    "height_max",
    "wood_density",
    "source_name",
    "source_citation",
    "source_url",
    "notes",
]


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in [".tsv", ".tab"]:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Create output df with required columns, defaulting to empty
    out = pd.DataFrame(columns=RAW_IMPORT_COLUMNS)
    for col in RAW_IMPORT_COLUMNS:
        out[col] = ""  # default blank

    # Copy what exists from input if present
    for col in ["species_name", "region", "component", "equation_type", "formula_text", "wood_density"]:
        if col in df.columns:
            out[col] = df[col].fillna("")

    # Defaults consistent with your current working pipeline:
    # - LOG_LINEAR_DBH uses DBH as predictor
    # - assume biomass in kg, DBH in cm unless later proven otherwise
    mask_dbh = out["equation_type"].astype(str).str.contains("DBH", na=False)
    out.loc[mask_dbh, "predictor_vars"] = "DBH"
    out.loc[mask_dbh, "biomass_units"] = "kg"
    out.loc[mask_dbh, "dbh_units"] = "cm"

    out["notes"] = out["notes"].where(out["notes"] != "", "Imported from GlobAllomeTree (staged); pending enrichment")

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize staged GlobAllomeTree table to app-ready schema.")
    parser.add_argument("input", type=str, help="Path to staged/original GlobAllomeTree table (CSV/TSV).")
    parser.add_argument("--out", type=str, default="", help="Optional explicit output path.")
    args = parser.parse_args()

    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    df = read_table(in_path)
    out_df = ensure_columns(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out).expanduser().resolve() if args.out else (PROCESSED_DIR / f"{in_path.stem}__normalized.csv")

    out_df.to_csv(out_path, index=False)

    print("=== GlobAllomeTree Normalize: APP-READY SCHEMA ===")
    print(f"Input:  {in_path}")
    print(f"Rows:   {len(out_df):,}")
    print(f"Wrote:  {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
