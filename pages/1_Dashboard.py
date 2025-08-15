
import streamlit as st
from utils.kpis import core_kpis, compare_kpis, compute_config_kpis
from utils.data_loader import sanitize
from app import header
import json
from datetime import datetime

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

header("Dashboard")

data = st.session_state.datasets
base_df = data.get("base")
cur_df  = data.get("cur")

if base_df is None or cur_df is None:
    st.warning("Upload links **Nulmeting** en **Actueel** om de monitoring te zien.")
    st.stop()

# Sanitize (no PII)
base_s = sanitize(base_df)
cur_s  = sanitize(cur_df)

# Core KPIs + delta
b = core_kpis(base_s); c = core_kpis(cur_s); d = compare_kpis(b,c)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Aantal clubs (actueel)", c["total_clubs"], delta=d.get("total_clubs"))
with col2:
    st.metric("Totaal leden", c["members_sum"] or 0, delta=(d.get("members_sum") or 0))
with col3:
    st.metric("Totaal vrijwilligers", c["volunteers_sum"] or 0, delta=(d.get("volunteers_sum") or 0))
with col4:
    pct = c["has_canteen_pct"]
    st.metric("% met kantine", f"{pct:.1f}%" if pct is not None else "—", delta=(f"{(d.get('has_canteen_pct') or 0):.1f}%" if d.get("has_canteen_pct") else None))

st.divider()

# Config KPIs
try:
    with open("config/kpis.json","r",encoding="utf-8") as f:
        KPI_SPEC = json.load(f)
except Exception:
    KPI_SPEC = []

conf_cur = compute_config_kpis(cur_s, base_s, KPI_SPEC)
conf_base = compute_config_kpis(base_s, base_s, KPI_SPEC) if base_s is not None else {}

st.markdown("### KPI's (config)")
cols = st.columns(4)
for i, item in enumerate(KPI_SPEC):
    label = item.get("label", item.get("key"))
    key = item.get("key")
    cur_val = conf_cur.get(key)
    base_val = conf_base.get(key) if conf_base else None
    delta = None
    if isinstance(cur_val,(int,float)) and isinstance(base_val,(int,float)):
        delta = cur_val - base_val
    with cols[i % 4]:
        if isinstance(cur_val, float) and "pct" in key.lower():
            cur_txt = f"{cur_val:.1f}%"
            delta_txt = (f"{delta:+.1f}%" if isinstance(delta,(int,float)) else None)
            st.metric(label, cur_txt, delta=delta_txt)
        else:
            st.metric(label, "—" if cur_val is None else cur_val, delta=None if delta is None else delta)

st.divider()

# Export: TXT-rapport
nowtxt = datetime.now().strftime("%Y-%m-%d %H:%M")
base_dt = data.get("base_date"); cur_dt = data.get("cur_date")
base_dt_txt = base_dt.strftime("%Y-%m-%d") if base_dt is not None else "Onbekend"
cur_dt_txt = cur_dt.strftime("%Y-%m-%d") if cur_dt is not None else "Onbekend"
lines = []
lines.append(f"Monitoring KPI-rapport — {nowtxt}")
lines.append(f"Peildatum nulmeting: {base_dt_txt}")
lines.append(f"Peildatum actueel:   {cur_dt_txt}")
lines.append("")
lines.append("[Core KPI's]")
lines.append(f"Aantal clubs (actueel): {c.get('total_clubs','-')} (Δ {d.get('total_clubs',0)})")
lines.append(f"Totaal leden: {c.get('members_sum','-')} (Δ {d.get('members_sum',0)})")
lines.append(f"Totaal vrijwilligers: {c.get('volunteers_sum','-')} (Δ {d.get('volunteers_sum',0)})")
pct_txt = '-' if c.get('has_canteen_pct') is None else f"{c.get('has_canteen_pct'):.1f}%"
delta_pct = d.get('has_canteen_pct')
delta_pct_txt = '' if delta_pct is None else f" (Δ {delta_pct:.1f}%)"
lines.append(f"% met kantine: {pct_txt}{delta_pct_txt}")
lines.append("")
if KPI_SPEC:
    lines.append("[Config KPI's]")
    for item in KPI_SPEC:
        key = item.get("key"); label = item.get("label", key)
        cv = conf_cur.get(key); bv = conf_base.get(key) if conf_base else None
        if isinstance(cv, float) and "pct" in key.lower():
            cv_txt = f"{cv:.1f}%"
            dv = (cv - bv) if isinstance(bv,(int,float)) else None
            dv_txt = f" (Δ {dv:+.1f}%)" if isinstance(dv,(int,float)) else ""
        else:
            cv_txt = "-" if cv is None else str(cv)
            dv = (cv - bv) if isinstance(cv,(int,float)) and isinstance(bv,(int,float)) else None
            dv_txt = f" (Δ {dv:+})" if isinstance(dv,(int,float)) else ""
        lines.append(f"{label}: {cv_txt}{dv_txt}")
report_txt = "\n".join(lines)
st.download_button("⬇️ Exporteer KPI-rapport (TXT)", data=report_txt, file_name="kpi_report.txt", mime="text/plain")

st.divider()

# Top-3 teksten
st.markdown("#### Top-3 Gemeenten (actueel)")
st.write(c["top_municipality"] or "—")

st.markdown("#### Top-3 Sporten (actueel)")
st.write(c["top_sport"] or "—")
