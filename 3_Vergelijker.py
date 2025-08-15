
import streamlit as st
from utils.kpis import field_differences, NON_PII_FIELDS
from utils.data_loader import sanitize, available_name_column

st.set_page_config(page_title="Vergelijker", page_icon="🆚", layout="wide")
from app import header

header("Vergelijker")

cur = st.session_state.datasets.get("cur")
if cur is None:
    st.info("Upload eerst het **Actueel** bestand links.")
    st.stop()

name_col = available_name_column(cur)
names = list(cur[name_col].dropna().unique())

colSel1, colSel2 = st.columns(2)
with colSel1:
    a_name = st.selectbox("Club A", names, key="cmp_a")
with colSel2:
    b_name = st.selectbox("Club B", names, key="cmp_b")

if a_name and b_name and a_name != b_name:
    a = cur[cur[name_col]==a_name].iloc[0]
    b = cur[cur[name_col]==b_name].iloc[0]
    diffs = field_differences(a,b)

    st.markdown(f"### {a_name}  ↔  {b_name}")
    st.caption("We vergelijken **geen PII** in deze weergave.")

    # Toon per veld een regel met verschil
    for field, txt in diffs.items():
        label = field.replace("_"," ").title()
        st.markdown(f"- **{label}**: {txt}")
else:
    st.info("Kies twee verschillende clubs om te vergelijken.")
