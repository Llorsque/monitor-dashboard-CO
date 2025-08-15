
import io
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from dateutil import parser as dateparser
from unidecode import unidecode

# Canonical column keys we aim for:
CANON = [
    "name","sport","municipality","federation",
    "street","postal_code","city",
    "contact_person","email","phone","role",
    "has_canteen","members_count","volunteers_count","membership_fee",
    "snapshot_date"
]

PII_COLS = {"contact_person","email","phone","role"}

# Synonym map (lowercased, stripped, ascii'd) -> canonical
SYNONYMS = {
    # name
    "clubnaam":"name","club":"name","vereniging":"name","organisatie":"name","naam":"name","relatie":"name",
    # sport
    "sport":"sport","sporttak":"sport","disciplines":"sport",
    # municipality / city
    "gemeente":"municipality","municipality":"municipality",
    "plaats":"city","stad":"city","woonplaats":"city","dorp":"city",
    # federation
    "sportsbond":"federation","bond":"federation","federatie":"federation",
    # address
    "straat + huisnummer":"street","straat en huisnummer":"street","adres":"street","straat":"street","huisnummer":"street",
    "postcode":"postal_code","post code":"postal_code",
    # contact / pii
    "contactpersoon":"contact_person","contact persoon":"contact_person","contact":"contact_person",
    "e-mail":"email","email":"email","mail":"email",
    "telefoonnummer":"phone","telefoon":"phone","mobiel":"phone","gsm":"phone",
    "functie":"role","rol":"role",
    # booleans
    "eigen kantine":"has_canteen","kantine":"has_canteen","heeft kantine":"has_canteen",
    # numerics
    "aantal leden":"members_count","leden":"members_count","leden_aantal":"members_count","totale leden":"members_count",
    "aantal vrijwilligers":"volunteers_count","vrijwilligers":"volunteers_count",
    "contributie":"membership_fee","lidmaatschap":"membership_fee","lidmaatschapskosten":"membership_fee","contributie per jaar":"membership_fee",
    # snapshot
    "peildatum":"snapshot_date","stand per":"snapshot_date","datum":"snapshot_date","snapshot":"snapshot_date"
}

def _canonize(col: str) -> str:
    key = unidecode(col or "").strip().lower()
    key = key.replace("\n"," ").replace("\r"," ").replace("  "," ")
    return SYNONYMS.get(key, key)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for c in df.columns:
        cc = _canonize(str(c))
        rename_map[c] = cc
    ndf = df.rename(columns=rename_map)
    return ndf

def _try_parse_date(val) -> Optional[pd.Timestamp]:
    if pd.isna(val): 
        return None
    if isinstance(val, (pd.Timestamp,)):
        return val
    if isinstance(val, (int,float)) and not np.isnan(val):
        # excel serial date
        try:
            return pd.to_datetime("1899-12-30") + pd.to_timedelta(int(val), unit="D")
        except Exception:
            pass
    try:
        return pd.to_datetime(dateparser.parse(str(val), dayfirst=True))
    except Exception:
        return None

def detect_snapshot(df: pd.DataFrame) -> Optional[pd.Timestamp]:
    for col in df.columns:
        cc = _canonize(str(col))
        if cc == "snapshot_date":
            series = df[col].dropna()
            if not series.empty:
                dt = _try_parse_date(series.iloc[0])
                if dt is not None:
                    return dt
    # try a single-cell dataframe with only date-like value
    # (noop here)
    return None

def _read_excel_or_csv(uploaded_file) -> pd.DataFrame:
    filename = getattr(uploaded_file, "name", "")
    bytes_data = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    if isinstance(bytes_data, (bytes, bytearray)):
        bio = io.BytesIO(bytes_data)
    else:
        # assume it's a path-like string
        with open(bytes_data, "rb") as f:
            bio = io.BytesIO(f.read())

    # Try Excel first
    try:
        df = pd.read_excel(bio, engine="openpyxl")
        return df
    except Exception:
        bio.seek(0)

    # Try Excel via python-calamine (robust) as a fallback
    try:
        bio.seek(0)
        df = pd.read_excel(bio, engine="calamine")
        return df
    except Exception:
        pass
            # Try CSV fallback
        try:
            df = pd.read_csv(bio, sep=None, engine="python")
            return df
        except Exception as e:
            raise RuntimeError(f"Kan bestand niet lezen als Excel of CSV: {e}")

def load_dataset(uploaded_file) -> tuple[pd.DataFrame, Optional[pd.Timestamp]]:
    raw = _read_excel_or_csv(uploaded_file)
    df = normalize_columns(raw)
    # strip whitespace and standardize booleans
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    if "has_canteen" in df.columns:
        df["has_canteen"] = df["has_canteen"].str.lower().map({
            "ja": True, "nee": False, "true": True, "false": False, "1": True, "0": False
        }).fillna(False)
    # numeric
    for col in ["members_count","volunteers_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    snap = detect_snapshot(df)
    return df, snap

def sanitize(df: pd.DataFrame) -> pd.DataFrame:
    return df[[c for c in df.columns if c not in PII_COLS]].copy()

def available_name_column(df: pd.DataFrame) -> str:
    for c in ["name","clubnaam","vereniging","organisatie","relatie","naam"]:
        if c in df.columns:
            return c
    # fallback: first column
    return df.columns[0]
