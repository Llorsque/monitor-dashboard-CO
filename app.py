
import streamlit as st
from datetime import datetime
from utils.data_loader import load_dataset, sanitize
from utils.schema import validate_dataset
import pandas as pd
import io

st.set_page_config(page_title="Monitoring Dashboard", page_icon="📊", layout="wide")
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Session state for datasets ---
if "datasets" not in st.session_state:
    st.session_state["datasets"] = {
        "base": None, "base_date": None, "base_name": None,
        "cur": None,  "cur_date":  None, "cur_name": None
    }

def upload_block():
    st.sidebar.subheader("📁 Data upload")
    base_up = st.sidebar.file_uploader("Nulmeting (.xlsx/.csv)", type=["xlsx","csv"], key="up_base")
    cur_up  = st.sidebar.file_uploader("Actueel (.xlsx/.csv)",   type=["xlsx","csv"], key="up_cur")
    info = st.sidebar.empty()

    if base_up is not None:
        try:
            df, snap = load_dataset(base_up)
            st.session_state.datasets["base"] = df
            st.session_state.datasets["base_date"] = snap
            st.session_state.datasets["base_name"] = base_up.name
            errors, warns = validate_dataset(df)
            if errors:
                info.error("Nulmeting: " + " | ".join(errors))
            if warns:
                info.warning("Nulmeting: " + " | ".join(warns))
            info.success("Nulmeting geladen.")
        except Exception as e:
            info.error(f"Fout bij laden nulmeting: {e}")

    if cur_up is not None:
        try:
            df, snap = load_dataset(cur_up)
            st.session_state.datasets["cur"] = df
            st.session_state.datasets["cur_date"] = snap
            st.session_state.datasets["cur_name"] = cur_up.name
            errors, warns = validate_dataset(df)
            if errors:
                info.error("Actueel: " + " | ".join(errors))
            if warns:
                info.warning("Actueel: " + " | ".join(warns))
            info.success("Actueel bestand geladen.")
        except Exception as e:
            info.error(f"Fout bij laden actueel: {e}")

    # helper: export sanitized data (optional)
    if st.sidebar.button("⬇️ Download monitoring dataset (actueel, zonder PII)"):
        cur = st.session_state.datasets["cur"]
        if cur is not None:
            s = sanitize(cur)
            csv = s.to_csv(index=False).encode("utf-8")
            st.sidebar.download_button("Download CSV", csv, file_name="actueel_sanitized.csv", mime="text/csv")

upload_block()

st.sidebar.markdown("---")
st.sidebar.caption("© Dashboard CO — gebouwd met Streamlit")
st.sidebar.caption("Kleur: #212945 • Accent: #52E8E8")

# Header component
def header(title: str):
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    base_dt = st.session_state.datasets.get("base_date")
    cur_dt  = st.session_state.datasets.get("cur_date")
    base_name = st.session_state.datasets.get("base_name") or "—"
    cur_name  = st.session_state.datasets.get("cur_name") or "—"

    col1, col2, col3, col4 = st.columns([3,2,2,2])
    with col1:
        st.markdown(f"### {title}")
        st.caption(f"**Nu:** {now}")
    with col2:
        st.markdown("Peildatum nulmeting")
        st.markdown(f"<div class='kpi-badge'>{base_dt.strftime('%d-%m-%Y') if base_dt else 'Onbekend'}</div>", unsafe_allow_html=True)
        st.caption(base_name)
    with col3:
        st.markdown("Peildatum actueel")
        st.markdown(f"<div class='kpi-badge'>{cur_dt.strftime('%d-%m-%Y') if cur_dt else 'Onbekend'}</div>", unsafe_allow_html=True)
        st.caption(cur_name)
    with col4:
        if st.session_state.datasets.get("base") is not None and st.session_state.datasets.get("cur") is not None:
            st.success("Bestanden geladen.")
        else:
            st.info("Upload links de bestanden.")

# Landing content
header("Dashboard")
st.markdown("Welkom! Gebruik het menu links om door de onderdelen te navigeren.\n- **Dashboard**: kerncijfers en verschillen\n- **Klantenkaart**: zoek details per club\n- **Vergelijker**: vergelijk 2 clubs\n- **Advanced**: kies eigen parameters & KPI\'s")
