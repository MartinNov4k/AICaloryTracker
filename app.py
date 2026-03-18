import streamlit as st
from openAI_apiCall import get_answer
import io, base64, json
from mimetypes import guess_type
import pandas as pd
import plotly.express as px
from datetime import date
from api_fce import get_Meal, post_meal, get_Targets
import json

st.set_page_config(
    page_title="Jídlovize",
    page_icon="🍽️",
    layout="centered"
)

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




## only for test case
USERS = {"admin": "123"}

if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.image("logo.png")
    st.header("Vyfoť jídlo, rozpoznej makra, sleduj svůj den.")

    st.subheader("🔑 Přihlášení")
    username = st.text_input("Uživatel")
    password = st.text_input("Heslo", type="password")

    if st.button("Přihlásit se"):
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            st.toast(f"✅ Přihlášen jako {username}")
            st.rerun()
        else:
            st.error("❌ Špatné jméno nebo heslo")
else:
    
    today = date.today().isoformat()

    api_url = r"https://marty1888.pythonanywhere.com/meals/"

  
    st.image("logo.png")

    #camera
    if "show_camera" not in st.session_state:
        st.session_state["show_camera"] = False

    if "photo" not in st.session_state:
        st.session_state["photo"] = None

    if st.button("Spustit kameru"):
        st.session_state["show_camera"] = True

    if st.session_state["show_camera"]:
        photo = st.camera_input("Vyfoť co jíš")
        st.session_state["photo"] = photo

        if st.button("vypnout kameru"):
            st.session_state["show_camera"] = False
            st.session_state["photo"] = None
            st.rerun()




    # Vstupy MUSÍ být mimo podmínky tlačítek
    
    note = st.text_area("Popiš jídlo nebo přidej fotku", "")
    user = st.session_state["user"]

    # Jedno akční tlačítko
    if st.button("Analyzovat jídlo a spočítat živiny"):
        if not st.session_state["photo"]:
            photo_bts = None
        else:
            photo_bts = photo.getvalue()

        with st.spinner("Počítám…"):
            try:
                result = get_answer(note, photo_bts)  # <— POZOR: bytes
                st.session_state["result"] = result
            except Exception as e:
                st.error(f"Chyba při volání modelu: {e}")
            else:
                # Výstup
                st.subheader("Souhrn")
                tot = result.get("total", {})
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Kalorie", f'{tot.get("calories", 0):.0f} kcal')
                col2.metric("Bílkoviny", f'{tot.get("protein_g", 0):.1f} g')
                col3.metric("Sacharidy", f'{tot.get("carbs_g", 0):.1f} g')
                col3.metric("Cukr", f'{tot.get("sugar_g", 0):.1f} g')
                col4.metric("Tuky", f'{tot.get("fat_g", 0):.1f} g')

                st.subheader("Položky")
                for it in result.get("items", []):
                    g = int(it.get("portion_grams", 0))
                    per100 = it.get("per_100g", {})
                    st.markdown(
                        f"- **{it.get('name','?')}** — ~{g} g  "
                        f"(na 100 g: {per100.get('calories',0):.0f} kcal, "
                        f"B {per100.get('protein_g',0):.1f} g, "
                        f"S {per100.get('carbs_g',0):.1f} g, "
                        f"T {per100.get('fat_g',0):.1f} g)"
                    )
                if result.get("assumptions"):
                    st.caption("Předpoklady: " + result["assumptions"])



    if "result" in st.session_state:
        if st.button("uložit"):
            result = st.session_state["result"]
            
            totals = result.get("total", {})
            totals["user"] = user

            item_name = ""
            for i, item in enumerate(result["items"]):
                if i > 0:
                    item_name += ", "
                item_name += item["name"]
            
            totals["name"] = item_name

            message = post_meal(api_url,totals)
            st.write(message)
                        
        if st.button("Zrušit"):
            st.session_state["result"] = None
            st.rerun()




    st.subheader("Denní přehled")
    
  
    
    day_data = get_Meal(user, today)
    targets_fromDB = get_Targets(user)

    if targets_fromDB:
        targets_fromDB = targets_fromDB[0] 

    else:
        targets_fromDB = {     ###default
            "protein_g": 150,
            "carbs_g": 275,
            "fat_g":70,
            "sugar_g":50,
            "calories":2000


        }

    
    
    

    if day_data:
        df = pd.DataFrame(day_data)
        cols = ["calories", "protein_g", "carbs_g", "fat_g", "sugar_g"]

        
        summary_df = pd.DataFrame([df[cols].sum()])


        st.dataframe(summary_df, hide_index=True)

        st.subheader("Dnes uložená jídla")
        df_to_show = df[cols +["name"]]
        st.dataframe(df_to_show, hide_index =True)

        ### pokus graf

        st.title("🍽️ Makroživiny")

        # Součty z dat
        totals = {
            "Bílkoviny": df["protein_g"].sum(),
            "Sacharidy": df["carbs_g"].sum(),
            "Tuky": df["fat_g"].sum(),
            "Cukry": df["sugar_g"].sum(),
            "Kalorie": df["calories"].sum()
        }

        # Cíle (můžeš si upravit nebo udělat vstup)
        targets = {
            "Bílkoviny": targets_fromDB["protein_g"],
            "Sacharidy":  targets_fromDB["carbs_g"],
            "Tuky": targets_fromDB["fat_g"],
            "Cukry": targets_fromDB["sugar_g"],
            "Kalorie": targets_fromDB["calories"],
        }

        def make_donut(label, value, target):
            remaining = max(target - value, 0)
            data = pd.DataFrame({
                "Stav": ["Snědeno", "Zbývá"],
                "g": [value, remaining]
            })

            g_label = ""
            if label != "Kalorie":
                g_label = "g"

            fig = px.pie(
                data, names="Stav", values="g", hole=0.6,
                color="Stav", color_discrete_map={"Snědeno": "green", "Zbývá": "lightgrey"},
                title=f"{label}: {int(value)} {g_label} / {int(target)} {g_label}"
            )
            fig.update_layout(
                showlegend=False,
                width=300, height=300,   # << menší velikost grafu
                margin=dict(t=50, b=20, l=20, r=20),
                title=dict(font=dict(size=16))  # menší titulek
            )
            return fig

        # 2 sloupce = 2 grafy na řádek

        st.plotly_chart(make_donut("Kalorie", totals["Kalorie"], targets["Kalorie"]), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(make_donut("Bílkoviny", totals["Bílkoviny"], targets["Bílkoviny"]), use_container_width=True)
        with col2:
            st.plotly_chart(make_donut("Sacharidy", totals["Sacharidy"], targets["Sacharidy"]), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(make_donut("Tuky", totals["Tuky"], targets["Tuky"]), use_container_width=True)
        with col4:
            st.plotly_chart(make_donut("Cukry", totals["Cukry"], targets["Cukry"]), use_container_width=True)
       
    else:
        st.write("pro dnešní den nejsou zatím žádné záznamy")
    if st.button("Nastavit cíle"):
        st.switch_page("pages/01_targets.py")

    if st.button("Historie"):
        st.switch_page("pages/02_history.py")