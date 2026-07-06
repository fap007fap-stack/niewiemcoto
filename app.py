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

# --- HOLIDAYS LOGIC ---
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
    holidays = {
        date(year, 1, 1): "Nowy Rok",
        date(year, 1, 6): "Trzech Króli",
        easter: "Wielkanoc",
        easter + timedelta(days=1): "Poniedziałek Wielkanocny",
        date(year, 5, 1): "Święto Pracy",
        date(year, 5, 3): "Święto Konstytucji 3 Maja",
        easter + timedelta(days=49): "Zielone Świątki",
        easter + timedelta(days=60): "Boże Ciało",
        date(year, 8, 15): "Wniebowzięcie NMP",
        date(year, 11, 1): "Wszystkich Świętych",
        date(year, 11, 11): "Święto Niepodległości",
        date(year, 12, 25): "Boże Narodzenie",
        date(year, 12, 26): "Boże Narodzenie",
    }
    return holidays

# --- DATABASE ---
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
        rows = conn.execute("SELECT date, person, color, created_at FROM days_off ORDER BY date ASC").fetchall()
    return {row[0]: {"person": row[1], "color": row[2], "created_at": row[3]} for row in rows}

def reserve_day(day: date, person: str, color: str):
    try:
        with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
            conn.execute("INSERT INTO days_off(date, person, color, created_at) VALUES (?, ?, ?, ?)",
                        (day.isoformat(), person, color, datetime.now().isoformat(timespec="seconds")))
            conn.commit()
        return True, "Zaznaczono dzień."
    except sqlite3.IntegrityError:
        return False, "Dzień zajęty."

def release_day(day: date, person: str):
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        current = conn.execute("SELECT person FROM days_off WHERE date = ?", (day.isoformat(),)).fetchone()
        if current and current[0] == person:
            conn.execute("DELETE FROM days_off WHERE date = ?", (day.isoformat(),))
            conn.commit()
            return True, "Odznaczono."
        return False, "Nie możesz tego zrobić."

# --- UI HELPERS ---
def text_color_for_bg(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#ffffff" if luminance < 0.55 else "#111827"

# --- PAGE SETUP ---
st.set_page_config(page_title="Poza biurem", page_icon="🗓️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .stApp { background: #000000; color: #ffffff; }
        .main .block-container { padding-top: 1rem; max-width: 1200px; }
        
        /* Form & Hero */
        .hero { padding: 20px; border-radius: 20px; background: #111111; border: 1px solid #333; margin-bottom: 15px; }
        .hero h1 { font-size: 32px; color: #ffffff; margin: 0; }
        .hero p { color: #888; font-size: 14px; margin: 5px 0 0 0; }
        
        .panel { padding: 15px; border-radius: 20px; background: #111111; border: 1px solid #333; margin-bottom: 15px; }
        
        /* Calendar Grid */
        .week-number { color: #555; font-size: 11px; font-weight: 800; text-align: center; padding-top: 15px; }
        .weekday { text-align: center; color: #ffffff; font-weight: 800; font-size: 12px; text-transform: uppercase; padding-bottom: 10px; }
        
        .day-container { position: relative; min-height: 90px; border-radius: 12px; border: 1px solid #222; background: #0a0a0a; margin-bottom: 5px; transition: 0.2s; overflow: hidden; }
        .day-container.weekend { background: #050505; border-color: #1a1a1a; opacity: 0.6; }
        .day-container.holiday { border-color: #442222; }
        .day-container.today { border: 2px solid #2563EB; }
        
        .day-header { display: flex; justify-content: space-between; padding: 5px 8px; font-size: 14px; font-weight: 900; }
        .holiday-name { font-size: 9px; color: #E11D48; position: absolute; bottom: 5px; left: 8px; font-weight: 700; text-transform: uppercase; }
        
        /* Reservation Overlay */
        .reservation-box { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 11px; font-weight: 900; text-align: center; padding: 5px;
            z-index: 2; pointer-events: none;
        }
        
        /* Button styling to fit inside */
        div.stButton > button {
            background: transparent; border: none; color: #444; width: 100%; height: 90px; 
            position: absolute; top: 0; left: 0; z-index: 1; margin: 0; padding: 0;
        }
        div.stButton > button:hover { background: rgba(255,255,255,0.05); color: #fff; }
        
        /* Input fields fix */
        .stSelectbox label, .stColorPicker label { color: #eee !important; font-weight: 700; }
        div[data-baseweb="select"] { background: #1a1a1a !important; border: 1px solid #333 !important; }
        input { background: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; }
        
        /* Login screen */
        .lock-card { max-width: 400px; margin: 15vh auto; padding: 40px; background: #111; border: 1px solid #333; border-radius: 30px; text-align: center; }
        .lock-card h3 { color: #fff; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
def main():
    init_db()
    
    if "authenticated" not in st.session_state:
        st.markdown('<div class="lock-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Kalendarz Firmowy")
        pwd = st.text_input("Hasło", type="password")
        if st.button("Wejdź", use_container_width=True):
            if hmac.compare_digest(pwd, APP_PASSWORD):
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Błędne hasło")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    today = date.today()
    st.session_state.setdefault("calendar_year", today.year)
    st.session_state.setdefault("calendar_month", today.month)
    
    # --- HEADER & SETTINGS ---
    st.markdown(f'<div class="hero"><h1>Kalendarz Poza Biurem</h1><p>Kliknij w kwadrat dnia, aby zarezerwować lub odznaczyć swoją obecność.</p></div>', unsafe_allow_html=True)
    
    col_set1, col_set2, col_set3 = st.columns([2, 1, 2])
    with col_set1:
        person = st.selectbox("Kto używa?", PEOPLE)
    with col_set2:
        color = st.color_picker("Kolor", DEFAULT_COLORS.get(person, "#2563EB"))
    
    events = get_all_events()
    holidays = get_polish_holidays(st.session_state.calendar_year)
    
    # --- NAVIGATION ---
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns([1, 3, 1, 1])
    with n1: 
        if st.button("←", key="prev"):
            st.session_state.calendar_month -= 1
            if st.session_state.calendar_month < 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            st.rerun()
    with n2: st.markdown(f"<h3 style='text-align:center; margin:0;'>{POLISH_MONTHS[st.session_state.calendar_month]} {st.session_state.calendar_year}</h3>", unsafe_allow_html=True)
    with n3:
        if st.button("→", key="next"):
            st.session_state.calendar_month += 1
            if st.session_state.calendar_month > 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            st.rerun()
    with n4:
        if st.button("Dzisiaj"):
            st.session_state.calendar_year, st.session_state.calendar_month = today.year, today.month
            st.rerun()

    # --- CALENDAR GRID ---
    cols = st.columns([0.5] + [1]*7)
    cols[0].markdown('<div class="weekday">Tydz</div>', unsafe_allow_html=True)
    for i, day_name in enumerate(WEEKDAYS):
        cols[i+1].markdown(f'<div class="weekday">{day_name}</div>', unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month)
    
    for week in month_days:
        w_cols = st.columns([0.5] + [1]*7)
        
        # Week number
        first_day_of_week = next((d for d in week if d != 0), None)
        if first_day_of_week:
            dt = date(st.session_state.calendar_year, st.session_state.calendar_month, first_day_of_week)
            week_num = dt.isocalendar()[1]
            w_cols[0].markdown(f'<div class="week-number">{week_num}</div>', unsafe_allow_html=True)
        
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i+1].markdown('<div style="min-height:90px;"></div>', unsafe_allow_html=True)
                continue
            
            cur_dt = date(st.session_state.calendar_year, st.session_state.calendar_month, day)
            iso = cur_dt.isoformat()
            is_weekend = i >= 5
            holiday_name = holidays.get(cur_dt)
            event = events.get(iso)
            
            classes = ["day-container"]
            if is_weekend: classes.append("weekend")
            if holiday_name: classes.append("holiday")
            if cur_dt == today: classes.append("today")
            
            with w_cols[i+1]:
                st.markdown(f'<div class="{" ".join(classes)}">', unsafe_allow_html=True)
                st.markdown(f'<div class="day-header"><span>{day}</span></div>', unsafe_allow_html=True)
                if holiday_name:
                    st.markdown(f'<div class="holiday-name">{holiday_name}</div>', unsafe_allow_html=True)
                
                if event:
                    owner = event["person"]
                    bg = event["color"]
                    tx = text_color_for_bg(bg)
                    st.markdown(f'<div class="reservation-box" style="background:{bg}; color:{tx};">{owner}</div>', unsafe_allow_html=True)
                    if st.button("", key=f"btn-{iso}"):
                        if owner == person:
                            release_day(cur_dt, person)
                            st.rerun()
                        else: st.toast(f"Zajęte przez: {owner}", icon="🚫")
                else:
                    if st.button("", key=f"btn-{iso}"):
                        reserve_day(cur_dt, person, color)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- FOOTER ---
    with st.expander("Legenda"):
        st.write("🔴 Dni świąteczne | 🌑 Weekendy (niepracujące) | 🟦 Dzisiaj")
        l_html = "".join([f'<span style="display:inline-block; padding:4px 10px; border-radius:10px; background:{c}; color:{text_color_for_bg(c)}; margin-right:5px; font-size:12px; font-weight:bold;">{p}</span>' for p,c in DEFAULT_COLORS.items()])
        st.markdown(l_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
