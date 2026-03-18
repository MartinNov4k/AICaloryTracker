import streamlit as st
from api_fce import get_Targets, post_target
import pandas as pd

st.markdown("""
<style>
    /* Skrytí horního defaultního pruhu Streamlitu */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
        height: 0px;
    }

    header[data-testid="stHeader"] * {
        display: none;
    }
</style>
""", unsafe_allow_html=True)



st.markdown("""

<style>

    /* ====== GLOBAL BACKGROUND ====== */
    .stApp {
        background: #f2f5f9 !important;
        color: #000 !important;
    }

    /* ====== SIDEBAR ====== */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        color: #000 !important;
        border-right: 1px solid #e5e7eb !important;
    }
    section[data-testid="stSidebar"] * {
        color: #000 !important;
    }

    /* ====== INPUTY (text_input, selectbox, number_input) ====== */
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        color: #000 !important;
        border-radius: 8px !important;
        border: 1px solid #d0d4da !important;
    }

    input, textarea, select {
        background-color: #ffffff !important;
        color: #000 !important;
    }

    /* Selectbox dropdown */
    ul[role="listbox"] {
        background: #ffffff !important;
        color: #000 !important;
    }
    li[role="option"] {
        color: #000 !important;
    }

    /* ====== TEXTY (nadpisy, labely, popisky) ====== */
    label, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #000 !important;
    }

    /* ====== BUTTON ====== */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: #fff !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        border: none !important;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
    }

    /* ====== TOASTY ====== */
    div[data-testid="stToast"] {
        background-color: #ffffff !important;
        color: #000 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    div[data-testid="stToast"] * {
        color: #000 !important;
    }

    /* ====== CARDS ====== */
    div[data-testid="stCard"] {
        background: #ffffff !important;
        border-radius: 10px !important;
    }

    /* ====== METRICS ====== */
    .stMetric {
        background: #ffffff !important;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

</style>
""", unsafe_allow_html=True)








if "user" not in st.session_state:
    st.error("Pro pokračování je nutné se přihlásit")
    st.stop()
user = st.session_state["user"]
targets = get_Targets(user)

if targets:
    df = pd.DataFrame(targets)

    df = df.drop("id", axis=1)

    st.write("Aktuální denní cíle")

    st.dataframe(df, use_container_width=True, hide_index=True)

st.write("Upravení denních cílů")

calories = st.number_input("Kalorie (kcal)", min_value=0, step=50, value=2000)
protein_g = st.number_input("Proteiny (g)", min_value=0, step=5, value=150)
carbs_g   = st.number_input("Sacharidy (g)", min_value=0, step=5, value=275)
fat_g     = st.number_input("Tuky (g)", min_value=0, step=1, value=70)
sugar_g   = st.number_input("Cukry (g)", min_value=0, step=1, value=50)

if st.button("Změnit cíle"):

    new_targets = {
    "user": user,
    "calories": calories,
    "protein_g": protein_g,
    "carbs_g": carbs_g,
    "fat_g": fat_g,
    "sugar_g": sugar_g
}

    message = post_target("https://marty1888.pythonanywhere.com/targets/", new_targets, user)

    st.write(message)
    st.rerun()
