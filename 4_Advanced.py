
import streamlit as st
import pandas as pd
from utils.data_loader import sanitize
from utils.kpis import core_kpis

st.set_page_config(page_title="Advanced", page_icon="⚙️", layout="wide")
from app import header

header("Advanced inzichten")

cur = st.session_state.datasets.get("cur")
base = st.session_state.datasets.get("base")

if cur is None:
    st.info("Upload eerst **Actueel** (en optioneel **Nulmeting**) links.")
    st.stop()

cur_s = sanitize(cur)
base_s = sanitize(base) if base is not None else None

st.markdown("Kies parameters en KPI\'s om inzichten te genereren. Geen tabellen/grafieken — alleen aantallen/percentages.")

with st.expander("🔧 Parameters & filters", expanded=True):
    group_by = st.multiselect("Groepeer op (max 2)", [c for c in ["municipality","sport","federation"] if c in cur_s.columns], max_selections=2)
    flt_muni = st.multiselect("Filter op Gemeente", sorted(cur_s.get("municipality", pd.Series([],dtype=object)).dropna().unique().tolist()) if "municipality" in cur_s.columns else [])
    flt_sport = st.multiselect("Filter op Sport", sorted(cur_s.get("sport", pd.Series([],dtype=object)).dropna().unique().tolist()) if "sport" in cur_s.columns else [])
    metric = st.selectbox("KPI", ["Aantal clubs","Totaal leden","Gemiddelde leden/club","Totaal vrijwilligers","Gemiddelde vrijwilligers/club","% met kantine"])

work = cur_s.copy()
if "municipality" in work.columns and len(flt_muni)>0:
    work = work[work["municipality"].isin(flt_muni)]
if "sport" in work.columns and len(flt_sport)>0:
    work = work[work["sport"].isin(flt_sport)]

def compute_metric(df, metric: str):
    if metric == "Aantal clubs":
        return len(df.index)
    if metric == "Totaal leden":
        return int(pd.to_numeric(df.get("members_count"), errors="coerce").sum(min_count=1) or 0)
    if metric == "Gemiddelde leden/club":
        return float(pd.to_numeric(df.get("members_count"), errors="coerce").mean() or 0)
    if metric == "Totaal vrijwilligers":
        return int(pd.to_numeric(df.get("volunteers_count"), errors="coerce").sum(min_count=1) or 0)
    if metric == "Gemiddelde vrijwilligers/club":
        return float(pd.to_numeric(df.get("volunteers_count"), errors="coerce").mean() or 0)
    if metric == "% met kantine":
        return float((df.get("has_canteen")==True).mean()*100) if "has_canteen" in df.columns else 0.0
    return 0

if len(group_by)==0:
    val = compute_metric(work, metric)
    st.markdown(f"### Resultaat: {val:.1f}" if isinstance(val,float) else f"### Resultaat: {val}")
else:
    # summary zonder tabel: we tonen per groep een regel "label: value (pct)"
    gb = work.groupby(group_by, dropna=False)
    totals = len(work.index)
    st.markdown("#### Resultaten per groep")
    lines = []
    for key, g in gb:
        label = " · ".join([str(x) if not pd.isna(x) else "Onbekend" for x in (key if isinstance(key, tuple) else (key,))])
        v = compute_metric(g, metric)
        pct = (len(g.index)/totals*100) if totals else 0
        if isinstance(v,float):
            lines.append(f"- **{label}**: {v:.1f}  ·  {len(g.index)} clubs  ·  {pct:.1f}% van totaal")
        else:
            lines.append(f"- **{label}**: {v}  ·  {len(g.index)} clubs  ·  {pct:.1f}% van totaal")
    st.markdown("\n".join(lines) if lines else "_Geen resultaten_")

st.info("Tip: Sla je keuzes op als preset via st.session_state in een toekomstige versie. We kunnen ook exports (CSV) toevoegen.")
