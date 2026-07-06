import calendar
import hmac
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

# --- CONFIG ---
APP_PASSWORD = os.getenv("APP_PASSWORD", "dexflex67")
DB_PATH = Path(__file__).with_name("out_of_office.db")

PEOPLE = ["Dagmara", "Szymon", "Michał", "Darek", "Julka"]

DEFAULT_COLORS = {
    "Dagmara": "#E11D48",
    "Szymon": "#2563EB",
    "Michał": "#16A34A",
    "Darek": "#F59E0B",
    "Julka": "#7C3AED",
}

WEEKDAYS = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]

# --- DB ---
def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS days_off (
                date TEXT PRIMARY KEY,
                person TEXT,
                color TEXT,
                created_at TEXT
            )
        """)
        conn.commit()

def get_events():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        rows = conn.execute("SELECT date, person, color FROM days_off").fetchall()
    return {r[0]: {"person": r[1], "color": r[2]} for r in rows}

def reserve(day, person, color):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        try:
            conn.execute(
                "INSERT INTO days_off VALUES (?, ?, ?, ?)",
                (day, person, color, datetime.now().isoformat())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

def release(day, person):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute("SELECT person FROM days_off WHERE date=?", (day,)).fetchone()
        if row and row[0] == person:
            conn.execute("DELETE FROM days_off WHERE date=?", (day,))
            conn.commit()

# --- COLOR TEXT ---
def text_color(bg):
    bg = bg.lstrip("#")
    r, g, b = int(bg[:2], 16), int(bg[2:4], 16), int(bg[4:], 16)
    return "#000" if (0.299*r + 0.587*g + 0.114*b) > 186 else "#fff"

# --- APP ---
st.set_page_config(layout="wide")

theme = st.sidebar.radio("Motyw", ["Ciemny", "Jasny"])
dark = theme == "Ciemny"

bg = "#000" if dark else "#fff"
fg = "#fff" if dark else "#111"
panel = "#111" if dark else "#f3f4f6"
border = "#333" if dark else "#ddd"

st.markdown(f"""
<style>
.stApp {{
    background:{bg};
    color:{fg};
}}

.calendar-btn {{
    width: 100%;
    height: 85px;
    border-radius: 12px;
    border: 1px solid {border};
    font-weight: 700;
    cursor: pointer;
}}

.calendar-btn:hover {{
    opacity: 0.85;
}}
</style>
""", unsafe_allow_html=True)

# --- INIT ---
init_db()

if "auth" not in st.session_state:
    pwd = st.text_input("Hasło", type="password")
    if st.button("Wejdź"):
        if hmac.compare_digest(pwd, APP_PASSWORD):
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Błędne hasło")
    st.stop()

# --- STATE ---
today = date.today()

st.session_state.setdefault("y", today.year)
st.session_state.setdefault("m", today.month)

person = st.selectbox("Osoba", PEOPLE)
color = st.color_picker("Kolor", DEFAULT_COLORS.get(person, "#2563EB"))

events = get_events()

# --- CLICK HANDLING (QUERY PARAM) ---
params = st.query_params

if "day" in params:
    day = params["day"]

    if day in events:
        if events[day]["person"] == person:
            release(day, person)
    else:
        reserve(day, person, color)

    st.query_params.clear()
    st.rerun()

# --- NAV ---
col1, col2, col3 = st.columns(3)

if col1.button("←"):
    st.session_state.m -= 1
    if st.session_state.m < 1:
        st.session_state.m = 12
        st.session_state.y -= 1
    st.rerun()

col2.markdown(f"### {st.session_state.m}/{st.session_state.y}")

if col3.button("→"):
    st.session_state.m += 1
    if st.session_state.m > 12:
        st.session_state.m = 1
        st.session_state.y += 1
    st.rerun()

# --- CALENDAR ---
cal = calendar.Calendar(firstweekday=0)
weeks = cal.monthdayscalendar(st.session_state.y, st.session_state.m)

st.write("")

header = st.columns(7)
for i, d in enumerate(WEEKDAYS):
    header[i].markdown(d)

for week in weeks:
    cols = st.columns(7)

    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
            continue

        d = date(st.session_state.y, st.session_state.m, day)
        iso = d.isoformat()

        ev = events.get(iso)

        if ev:
            bgc = ev["color"]
            txt = text_color(bgc)
            label = f"{day}<br>{ev['person']}"
        else:
            bgc = "#222" if dark else "#eee"
            txt = "#fff" if dark else "#111"
            label = str(day)

        html = f"""
        <a href="?day={iso}" style="text-decoration:none">
            <button class="calendar-btn"
                style="
                    background:{bgc};
                    color:{txt};
                ">
                {label}
            </button>
        </a>
        """

        cols[i].markdown(html, unsafe_allow_html=True)
