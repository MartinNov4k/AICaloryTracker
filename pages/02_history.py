import streamlit as st
from api_fce import get_history
import pandas as pd
from datetime import date, timedelta

if "user" not in st.session_state:
    st.error("Pro pokračování je nutné se přihlásit")
    st.stop()
user = st.session_state["user"]

today = date.today()
yestrday_raw = today - timedelta(days=1)

yestrday = yestrday_raw.isoformat()

st.header("Včera")
st.write(yestrday)



yestrday_data = get_history("https://marty1888.pythonanywhere.com/meals/",user, yestrday )

if yestrday_data :
    df = pd.DataFrame(yestrday_data)

    df = df.drop(columns = ["created_at", "user", "id"])
    agg = df.agg({
        "calories": "sum",
        "protein_g": "sum",
        "fat_g": "sum",
        "carbs_g": "sum",
        "sugar_g": "sum"

    })
    st.dataframe(df, hide_index=True)

    st.dataframe(agg.to_frame(name="total"))

else:
    st.write(f"Pro tento den nejsou data")