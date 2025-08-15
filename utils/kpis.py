
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np

SAFE_DEFAULTS = {
    "name": "",
    "sport": "",
    "municipality": "",
    "federation": "",
    "street": "",
    "postal_code": "",
    "city": "",
    "has_canteen": False,
    "members_count": pd.NA,
    "volunteers_count": pd.NA,
    "membership_fee": pd.NA,
}

NON_PII_FIELDS = [
    "name","sport","municipality","federation","street","postal_code","city",
    "has_canteen","members_count","volunteers_count","membership_fee"
]

def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    for k, v in SAFE_DEFAULTS.items():
        if k not in df.columns:
            df[k] = v
    return df

def core_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute basic counts & percentages for one dataset."""
    df = _ensure_cols(df)
    total = len(df.index)
    members_sum = pd.to_numeric(df["members_count"], errors="coerce").sum(min_count=1)
    members_avg = pd.to_numeric(df["members_count"], errors="coerce").mean()
    volunteers_sum = pd.to_numeric(df["volunteers_count"], errors="coerce").sum(min_count=1)
    volunteers_avg = pd.to_numeric(df["volunteers_count"], errors="coerce").mean()
    has_canteen_pct = float((df["has_canteen"]==True).mean()*100) if "has_canteen" in df.columns else None

    # top-3 municipality / sport (text-friendly)
    def top3_text(series: pd.Series) -> str:
        if series.empty:
            return "-"
        s = series.fillna("Onbekend").value_counts(normalize=False)
        total = s.sum()
        items = []
        for idx, cnt in s.head(3).items():
            pct = (cnt/total)*100 if total else 0
            items.append(f"{idx}: {cnt} ({pct:.1f}%)")
        return " · ".join(items) if items else "-"

    top_muni = top3_text(df.get("municipality", pd.Series([], dtype=object)))
    top_sport = top3_text(df.get("sport", pd.Series([], dtype=object)))

    return {
        "total_clubs": int(total),
        "members_sum": None if pd.isna(members_sum) else int(members_sum),
        "members_avg": None if pd.isna(members_avg) else float(members_avg),
        "volunteers_sum": None if pd.isna(volunteers_sum) else int(volunteers_sum),
        "volunteers_avg": None if pd.isna(volunteers_avg) else float(volunteers_avg),
        "has_canteen_pct": None if has_canteen_pct is None else float(has_canteen_pct),
        "top_municipality": top_muni,
        "top_sport": top_sport,
    }

def compare_kpis(base: Dict[str, Any], cur: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Return deltas (cur - base) for overlapping KPIs."""
    deltas = {}
    keys = set(base.keys()).intersection(cur.keys())
    for k in keys:
        b = base[k]; c = cur[k]
        if isinstance(b, (int,float)) and isinstance(c, (int,float)):
            deltas[k] = c - b
    return deltas

def field_differences(a: pd.Series, b: pd.Series) -> Dict[str, str]:
    """Human-readable field-by-field difference (non-PII)."""
    out = {}
    for col in NON_PII_FIELDS:
        if col in a.index or col in b.index:
            va = a.get(col, "")
            vb = b.get(col, "")
            if pd.isna(va): va = ""
            if pd.isna(vb): vb = ""
            if str(va) != str(vb):
                out[col] = f"{va} → {vb}"
            else:
                out[col] = "—"
    return out


def _pct_true(series: pd.Series) -> float:
    if series is None or len(series.index)==0:
        return 0.0
    return float((series==True).mean()*100)

def compute_config_kpis(df: pd.DataFrame, baseline: Optional[pd.DataFrame], spec: list[dict]) -> dict:
    """Compute KPIs from a config spec list."""
    out = {}
    # helper sets
    names_df = set(df.get("name", pd.Series([],dtype=object)).dropna().astype(str).str.strip().unique())
    names_base = set(baseline.get("name", pd.Series([],dtype=object)).dropna().astype(str).str.strip().unique()) if baseline is not None else set()

    for item in spec:
        t = item.get("type")
        key = item.get("key")
        col = item.get("column")
        if t == "count_rows":
            out[key] = int(len(df.index))
        elif t == "sum" and col in df.columns:
            out[key] = int(pd.to_numeric(df[col], errors="coerce").sum(min_count=1) or 0)
        elif t == "mean" and col in df.columns:
            m = pd.to_numeric(df[col], errors="coerce").mean()
            out[key] = None if pd.isna(m) else float(m)
        elif t == "pct_true" and col in df.columns:
            out[key] = float(_pct_true(df[col]))
        elif t == "count_new_names":
            if baseline is None:
                out[key] = None
            else:
                out[key] = int(len(names_df - names_base))
        else:
            out[key] = None
    return out
