
from __future__ import annotations
from typing import List, Dict, Tuple
import pandas as pd

# Canonical fields
REQUIRED_FIELDS = ["name"]
RECOMMENDED_FIELDS = ["sport","municipality","has_canteen","members_count","volunteers_count","snapshot_date"]

PII_FIELDS = ["contact_person","email","phone","role"]

NUMERIC_FIELDS = ["members_count","volunteers_count","membership_fee"]
BOOLEAN_FIELDS = ["has_canteen"]

def validate_dataset(df: pd.DataFrame) -> Tuple[list[str], list[str]]:
    """Return (errors, warnings) based on schema checks. df is expected to be canonicalized already."""
    errors: list[str] = []
    warnings: list[str] = []

    # required
    for f in REQUIRED_FIELDS:
        if f not in df.columns:
            errors.append(f"Verplicht veld ontbreekt: '{f}'")
    # recommended
    for f in RECOMMENDED_FIELDS:
        if f not in df.columns:
            warnings.append(f"Aanbevolen veld ontbreekt: '{f}'")

    # datatypes (best-effort)
    for f in NUMERIC_FIELDS:
        if f in df.columns:
            bad = pd.to_numeric(df[f], errors="coerce").isna() & df[f].notna()
            if bad.any():
                warnings.append(f"Veld '{f}' bevat {int(bad.sum())} niet-numerieke waardes.")
    for f in BOOLEAN_FIELDS:
        if f in df.columns:
            ok = df[f].isin([True, False])
            if (~ok & df[f].notna()).any():
                warnings.append(f"Veld '{f}' bevat waarden die niet Ja/Nee (True/False) zijn.")

    # uniqueness (name advisable)
    if "name" in df.columns:
        dups = df["name"].astype(str).str.strip().duplicated(keep=False)
        if dups.any():
            warnings.append(f"'{ 'name' }' bevat {int(dups.sum())} dubbele waarden.")

    return errors, warnings
