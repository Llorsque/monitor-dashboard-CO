
import streamlit as st
from utils.data_loader import available_name_column

st.set_page_config(page_title="Klantenkaart", page_icon="🗂️", layout="wide")
from app import header

header("Klantenkaart")

cur = st.session_state.datasets.get("cur")
if cur is None:
    st.info("Upload eerst het **Actueel** bestand links.")
    st.stop()

name_col = available_name_column(cur)

st.markdown("Zoek op club/klant")
q = st.text_input("Naam bevat:", value="", placeholder="Typ (deel van) de naam...")
options = cur[cur[name_col].str.contains(q, case=False, na=False)][name_col].unique()[:50]
sel = st.selectbox("Selecteer club", ["— kies —"] + list(options))

if sel and sel != "— kies —":
    row = cur[cur[name_col] == sel].iloc[0]
    st.markdown(f"### {sel}")
    # Toon alle beschikbare velden, inclusief PII
    non_empty = {k: v for k, v in row.to_dict().items() if str(v).strip() not in ["", "nan", "NaN", "None"]}
    # Kolomsgewijze listing (key-value)
    cols = st.columns(2)
    items = list(non_empty.items())
    half = (len(items)+1)//2
    with cols[0]:
        for k, v in items[:half]:
            st.markdown(f"**{k}**")
            st.write(f"{v}")
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    with cols[1]:
        for k, v in items[half:]:
            st.markdown(f"**{k}**")
            st.write(f"{v}")
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
