import calendar
import hmac
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

# --- CONFIGURATION ---
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

POLISH_MONTHS = {
    1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień", 5: "Maj", 6: "Czerwiec",
    7: "Lipiec", 8: "Sierpień", 9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"
}

WEEKDAYS = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]

# --- HOLIDAYS ---
def get_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def get_polish_holidays(year):
    easter = get_easter(year)
    return {
        date(year, 1, 1): "Nowy Rok",
        date(year, 1, 6): "Trzech Króli",
        easter: "Wielkanoc",
        easter + timedelta(days=1): "Poniedziałek Wielkanocny",
        date(year, 5, 1): "Święto Pracy",
        date(year, 5, 3): "Święto Konstytucji",
        easter + timedelta(days=49): "Zielone Świątki",
        easter + timedelta(days=60): "Boże Ciało",
        date(year, 8, 15): "Wniebowzięcie NMP",
        date(year, 11, 1): "Wszystkich Świętych",
        date(year, 11, 11): "Niepodległość",
        date(year, 12, 25): "Boże Narodzenie",
        date(year, 12, 26): "Boże Narodzenie",
    }

# --- DB ---
def init_db():
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS days_off (
                date TEXT PRIMARY KEY,
                person TEXT NOT NULL,
                color TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def get_all_events():
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        rows = conn.execute(
            "SELECT date, person, color FROM days_off ORDER BY date"
        ).fetchall()
    return {r[0]: {"person": r[1], "color": r[2]} for r in rows}

def reserve_day(day, person, color):
    try:
        with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
            conn.execute(
                "INSERT INTO days_off VALUES (?, ?, ?, ?)",
                (day.isoformat(), person, color, datetime.now().isoformat())
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def release_day(day, person):
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        row = conn.execute(
            "SELECT person FROM days_off WHERE date=?",
            (day.isoformat(),)
        ).fetchone()

        if row and row[0] == person:
            conn.execute("DELETE FROM days_off WHERE date=?", (day.isoformat(),))
            conn.commit()
            return True
        return False

# --- COLORS ---
def text_color(bg):
    bg = bg.lstrip("#")
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    return "#000000" if (0.299*r + 0.587*g + 0.114*b) > 186 else "#ffffff"

# --- APP ---
st.set_page_config(page_title="Kalendarz", layout="wide")

theme = st.sidebar.radio("Motyw", ["Ciemny", "Jasny"])
dark = theme == "Ciemny"

bg = "#000" if dark else "#fff"
fg = "#fff" if dark else "#111"
panel = "#111" if dark else "#f3f4f6"
border = "#333" if dark else "#ddd"

st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {fg};
}}

.panel {{
    background: {panel};
    border: 1px solid {border};
    padding: 10px;
    border-radius: 15px;
}}

.day {{
    border-radius: 12px;
}}

div.stButton > button {{
    width: 100%;
    height: 85px;
    border-radius: 12px;
    background: {panel};
    color: {fg};
    border: 1px solid {border};
}}

div.stButton > button:hover {{
    opacity: 0.85;
}}

</style>
""", unsafe_allow_html=True)

def main():
    init_db()

    if "auth" not in st.session_state:
        pwd = st.text_input("Hasło", type="password")
        if st.button("Wejdź"):
            if hmac.compare_digest(pwd, APP_PASSWORD):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Błędne hasło")
        return

    today = date.today()
    st.session_state.setdefault("y", today.year)
    st.session_state.setdefault("m", today.month)

    person = st.selectbox("Osoba", PEOPLE)
    color = st.color_picker("Kolor", DEFAULT_COLORS.get(person, "#2563EB"))

    events = get_all_events()
    holidays = get_polish_holidays(st.session_state.y)

    col1, col2, col3 = st.columns(3)
    if col1.button("←"):
        st.session_state.m -= 1
        if st.session_state.m < 1:
            st.session_state.m = 12
            st.session_state.y -= 1
        st.rerun()

    col2.markdown(f"### {POLISH_MONTHS[st.session_state.m]} {st.session_state.y}")

    if col3.button("→"):
        st.session_state.m += 1
        if st.session_state.m > 12:
            st.session_state.m = 1
            st.session_state.y += 1
        st.rerun()

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(st.session_state.y, st.session_state.m)

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

            event = events.get(iso)
            holiday = holidays.get(d)

            label = str(day)

            if event:
                label = f"{day}\n{event['person']}"
            elif holiday:
                label = f"{day}\n{holiday}"

            if cols[i].button(label, key=iso):
                if event:
                    if event["person"] == person:
                        release_day(d, person)
                    else:
                        st.toast("Zajęte")
                else:
                    reserve_day(d, person, color)

                st.rerun()

if __name__ == "__main__":
    main()
