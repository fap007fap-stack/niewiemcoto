import streamlit as st
import calendar
import json
import os
from datetime import date, datetime
from collections import defaultdict

st.set_page_config(
    page_title="Kalendarz Zespołu",
    layout="wide"
)

PASSWORD = "dexflex67"

USERS = {
    "Dagmara": "#ff5c8d",
    "Julia": "#b05cff",
    "Darek": "#4da6ff",
    "Szymon": "#45d483",
    "Michał": "#ffb347"
}

DATA_FILE = "calendar_data.json"


# ---------- Hasło ----------

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:

    st.title("🔒 Kalendarz Zespołowy")

    password = st.text_input(
        "Podaj hasło",
        type="password"
    )

    if st.button("Zaloguj"):
        if password == PASSWORD:
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("Niepoprawne hasło")

    st.stop()

# ---------- Dane ----------

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf8") as f:
        data = json.load(f)
else:
    data = {}

# ---------- Styl ----------

st.markdown("""
<style>

div.stButton>button{
width:100%;
height:75px;
font-size:15px;
border-radius:10px;
}

.dayBox{
border-radius:10px;
padding:6px;
height:85px;
font-size:14px;
font-weight:bold;
}

.weekLabel{
font-weight:bold;
font-size:18px;
padding-top:25px;
}

.month{
font-size:34px;
font-weight:bold;
padding-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# ---------- Wybór ----------

today = date.today()

c1,c2,c3 = st.columns([2,2,6])

with c1:
    year = st.number_input(
        "Rok",
        value=today.year,
        step=1
    )

with c2:
    month = st.selectbox(
        "Miesiąc",
        list(range(1,13)),
        index=today.month-1,
        format_func=lambda x: calendar.month_name[x]
    )

person = st.selectbox(
    "Wybierz osobę",
    list(USERS.keys())
)

st.markdown(
    f"<div class='month'>{calendar.month_name[month]} {year}</div>",
    unsafe_allow_html=True
)

weekdays = [
    "",
    "Pon",
    "Wt",
    "Śr",
    "Czw",
    "Pt",
    "Sob",
    "Nd"
]

cols = st.columns(8)

for i,w in enumerate(weekdays):
    cols[i].markdown(f"### {w}")

cal = calendar.Calendar(firstweekday=0)

weeks = cal.monthdatescalendar(year,month)

for week in weeks:

    week_number = week[0].isocalendar()[1]

    cols = st.columns(8)

    cols[0].markdown(
        f"<div class='weekLabel'>W{week_number}</div>",
        unsafe_allow_html=True
    )

    for i,day in enumerate(week):

        if day.month != month:
            cols[i+1].write("")
            continue

        key = str(day)

        if key in data:

            owner = data[key]
            color = USERS[owner]

            cols[i+1].markdown(f"""
            <div class="dayBox"
            style="
            background:{color};
            color:white;
            ">
            <b>{day.day}</b><br><br>
            {owner}
            </div>
            """,
            unsafe_allow_html=True)

        else:

            if cols[i+1].button(
                f"{day.day}",
                key=key
            ):
                data[key]=person

                with open(DATA_FILE,"w",encoding="utf8") as f:
                    json.dump(data,f)

                st.rerun()

st.divider()

st.subheader("Usuwanie swoich rezerwacji")

own = []

for d,u in data.items():
    if u==person:

        dt=datetime.strptime(d,"%Y-%m-%d")

        own.append((dt,d))

own.sort()

for dt,d in own:

    c1,c2=st.columns([4,1])

    c1.write(dt.strftime("%d.%m.%Y"))

    if c2.button("Usuń",key="del"+d):

        del data[d]

        with open(DATA_FILE,"w",encoding="utf8") as f:
            json.dump(data,f)

        st.rerun()
