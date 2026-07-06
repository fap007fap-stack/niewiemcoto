import calendar
import hmac
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path

import streamlit as st

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
    1: "Styczeń",
    2: "Luty",
    3: "Marzec",
    4: "Kwiecień",
    5: "Maj",
    6: "Czerwiec",
    7: "Lipiec",
    8: "Sierpień",
    9: "Wrzesień",
    10: "Październik",
    11: "Listopad",
    12: "Grudzień",
}
WEEKDAYS = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]


st.set_page_config(
    page_title="Poza biurem",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        :root {
            --card-bg: rgba(255, 255, 255, 0.78);
            --stroke: rgba(15, 23, 42, 0.10);
            --soft: rgba(15, 23, 42, 0.06);
            --text: #0f172a;
            --muted: #64748b;
        }

        .stApp {
             background: #000000;
            color: var(--text);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        .hero {
            padding: 28px 30px;
            border: 1px solid var(--stroke);
            border-radius: 28px;
            background: rgba(255,255,255,0.72);
            box-shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
            backdrop-filter: blur(16px);
            margin-bottom: 20px;
        }

        .hero h1 {
            margin: 0;
            font-size: 42px;
            line-height: 1.05;
            letter-spacing: -0.04em;
            color: var(--text);
        }

        .hero p {
            color: var(--muted);
            margin-top: 10px;
            font-size: 17px;
        }

        .panel {
            padding: 20px;
            border: 1px solid var(--stroke);
            border-radius: 24px;
            background: rgba(255,255,255,0.72);
            box-shadow: 0 14px 45px rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(14px);
            margin-bottom: 18px;
        }

        .weekday {
            text-align: center;
            color: #ffffff;
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 8px 0 12px 0;
        }

        .day-card {
            min-height: 126px;
            border: 1px solid var(--stroke);
            border-radius: 20px;
            background: rgba(255,255,255,0.72);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            padding: 13px 13px 10px 13px;
            margin-bottom: 8px;
        }

        .day-card.today {
            outline: 3px solid rgba(37, 99, 235, 0.18);
            border-color: rgba(37, 99, 235, 0.35);
        }

        .day-number {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #ffffff;
            font-weight: 900;
            font-size: 17px;
        }

        .chip-free,
        .chip-taken,
        .chip-mine {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 12px;
            border-radius: 999px;
            padding: 8px 10px;
            font-size: 13px;
            font-weight: 800;
            max-width: 100%;
        }

        .chip-free {
            background: rgba(16, 185, 129, 0.12);
            color: #047857;
        }

        .chip-taken {
            color: #111827;
            box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.08);
        }

        .chip-mine {
            color: #111827;
            box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.08);
        }

        .empty-day {
            min-height: 126px;
            border: 1px dashed rgba(15, 23, 42, 0.10);
            border-radius: 20px;
            background: rgba(255,255,255,0.32);
            margin-bottom: 8px;
        }

        .metric-card {
            border: 1px solid var(--stroke);
            border-radius: 20px;
            background: rgba(255,255,255,0.62);
            padding: 16px;
            min-height: 94px;
        }

        .metric-card .label {
            color: #64748b;
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-card .value {
            color: #0f172a;
            font-size: 30px;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-top: 2px;
        }

        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border: 1px solid var(--stroke);
            border-radius: 999px;
            padding: 9px 12px;
            margin: 0 8px 8px 0;
            background: rgba(255,255,255,0.65);
            font-weight: 800;
            color: #0f172a;
        }

        .dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            display: inline-block;
        }

        div.stButton > button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(15, 23, 42, 0.10);
            background: rgba(255,255,255,0.86);
            font-weight: 850;
            color: #0f172a;
            min-height: 38px;
            transition: all 0.15s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(37, 99, 235, 0.45);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.12);
        }

        .small-note {
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
        }

        .lock-card {
            max-width: 520px;
            margin: 8vh auto 0 auto;
            padding: 30px;
            border: 1px solid var(--stroke);
            border-radius: 30px;
            background: rgba(255,255,255,0.76);
            box-shadow: 0 28px 80px rgba(15, 23, 42, 0.12);
            backdrop-filter: blur(16px);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_db() -> None:
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS days_off (
                date TEXT PRIMARY KEY,
                person TEXT NOT NULL,
                color TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_all_events() -> dict[str, dict[str, str]]:
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        rows = conn.execute(
            "SELECT date, person, color, created_at FROM days_off ORDER BY date ASC"
        ).fetchall()
    return {
        row[0]: {
            "person": row[1],
            "color": row[2],
            "created_at": row[3],
        }
        for row in rows
    }


def reserve_day(day: date, person: str, color: str) -> tuple[bool, str]:
    try:
        with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
            conn.execute(
                "INSERT INTO days_off(date, person, color, created_at) VALUES (?, ?, ?, ?)",
                (day.isoformat(), person, color, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()
        return True, "Zaznaczono dzień poza biurem."
    except sqlite3.IntegrityError:
        return False, "Ten dzień jest już zajęty przez inną osobę."


def release_day(day: date, person: str) -> tuple[bool, str]:
    with closing(sqlite3.connect(DB_PATH, timeout=20)) as conn:
        current = conn.execute(
            "SELECT person FROM days_off WHERE date = ?", (day.isoformat(),)
        ).fetchone()
        if current is None:
            return False, "Ten dzień nie jest już zaznaczony."
        if current[0] != person:
            return False, "Możesz odznaczyć tylko swój własny dzień."
        conn.execute("DELETE FROM days_off WHERE date = ?", (day.isoformat(),))
        conn.commit()
    return True, "Odznaczono dzień."


def month_events(events: dict[str, dict[str, str]], year: int, month: int) -> dict[str, dict[str, str]]:
    prefix = f"{year:04d}-{month:02d}-"
    return {key: value for key, value in events.items() if key.startswith(prefix)}


def text_color_for_bg(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except Exception:
        return "#ffffff"
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#ffffff" if luminance < 0.55 else "#111827"


def polish_date_label(iso_date: str) -> str:
    parsed = datetime.fromisoformat(iso_date).date()
    return f"{parsed.day:02d}.{parsed.month:02d}.{parsed.year}"


def password_gate() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown('<div class="lock-card">', unsafe_allow_html=True)
    st.markdown("### 🔐 Wejście do kalendarza")
    st.caption("Podaj hasło, żeby zobaczyć i edytować dni poza biurem.")

    password = st.text_input("Hasło", type="password", placeholder="Wpisz hasło")
    enter = st.button("Wejdź", use_container_width=True)

    if enter:
        if hmac.compare_digest(password, APP_PASSWORD):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Nieprawidłowe hasło.")

    st.markdown("</div>", unsafe_allow_html=True)
    return False


def change_month(delta: int) -> None:
    year = st.session_state.calendar_year
    month = st.session_state.calendar_month + delta
    if month < 1:
        month = 12
        year -= 1
    if month > 12:
        month = 1
        year += 1
    st.session_state.calendar_year = year
    st.session_state.calendar_month = month


def set_current_month() -> None:
    today = date.today()
    st.session_state.calendar_year = today.year
    st.session_state.calendar_month = today.month


def render_day(day: int, year: int, month: int, selected_person: str, selected_color: str, events: dict[str, dict[str, str]]) -> None:
    if day == 0:
        st.markdown('<div class="empty-day"></div>', unsafe_allow_html=True)
        return

    current_day = date(year, month, day)
    iso = current_day.isoformat()
    event = events.get(iso)
    today_class = " today" if current_day == date.today() else ""

    st.markdown(
        f"""
        <div class="day-card{today_class}">
            <div class="day-number">
                <span>{day}</span>
                <span style="font-size: 12px; color: #ffffff; font-weight: 800;">{POLISH_MONTHS[month][:3]}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if event:
        owner = event["person"]
        color = event["color"]
        label = "Twój dzień" if owner == selected_person else "Zajęte"
        class_name = "chip-mine" if owner == selected_person else "chip-taken"
        txt_color = text_color_for_bg(color)
        st.markdown(
            f"""
            <div class="{class_name}" style="background: {color}; color: {txt_color};">
                <span>●</span><span>{label}: {owner}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="chip-free">✓ Wolne</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if event and event["person"] == selected_person:
        if st.button("Odznacz", key=f"remove-{iso}"):
            ok, msg = release_day(current_day, selected_person)
            if ok:
                st.toast(msg, icon="✅")
            else:
                st.toast(msg, icon="⚠️")
            st.rerun()
    elif event:
        st.button("Zablokowane", key=f"blocked-{iso}", disabled=True)
    else:
        if st.button("Zaznacz", key=f"add-{iso}"):
            ok, msg = reserve_day(current_day, selected_person, selected_color)
            if ok:
                st.toast(msg, icon="✅")
            else:
                st.toast(msg, icon="⚠️")
            st.rerun()


def main() -> None:
    init_db()

    if not password_gate():
        return

    today = date.today()
    st.session_state.setdefault("calendar_year", today.year)
    st.session_state.setdefault("calendar_month", today.month)

    st.markdown(
        """
        <div class="hero">
            <h1>Kalendarz poza biurem</h1>
            <p>Wybierz osobę, kolor i zaznacz dzień. Jeśli dzień jest już zajęty, nikt inny nie może go wybrać, dopóki właściciel go nie odznaczy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    settings_left, settings_right = st.columns([1.15, 0.85], gap="large")

    with settings_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        person = st.selectbox("Kto zaznacza dzień?", PEOPLE, index=0)
        color = st.color_picker("Twój kolor na kalendarzu", DEFAULT_COLORS.get(person, "#2563EB"))
        st.markdown("</div>", unsafe_allow_html=True)

    events = get_all_events()
    current_month_events = month_events(events, st.session_state.calendar_year, st.session_state.calendar_month)
    mine_this_month = sum(1 for item in current_month_events.values() if item["person"] == person)
    taken_this_month = len(current_month_events)

    with settings_right:
        metric_a, metric_b = st.columns(2)
        with metric_a:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Zajęte w miesiącu</div>
                    <div class="value">{taken_this_month}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with metric_b:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">Twoje dni</div>
                    <div class="value">{mine_this_month}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            '<p class="small-note">Podgląd odświeża się po każdej zmianie. SQLite pilnuje, żeby jeden dzień mógł mieć tylko jednego właściciela.</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    nav_left, nav_mid, nav_right, nav_today = st.columns([1, 2, 1, 1])
    with nav_left:
        st.button("← Poprzedni", on_click=change_month, args=(-1,), use_container_width=True)
    with nav_mid:
        st.markdown(
            f"<h2 style='text-align:center; margin: 4px 0 0 0; letter-spacing: -0.03em; color: #ffffff;'>{POLISH_MONTHS[st.session_state.calendar_month]} {st.session_state.calendar_year}</h2>",
            unsafe_allow_html=True,
        )
    with nav_right:
        st.button("Następny →", on_click=change_month, args=(1,), use_container_width=True)
    with nav_today:
        st.button("Dzisiaj", on_click=set_current_month, use_container_width=True)

    header_cols = st.columns(7)
    for col, weekday in zip(header_cols, WEEKDAYS):
        with col:
            st.markdown(f'<div class="weekday">{weekday}</div>', unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month):
        cols = st.columns(7)
        for col, day in zip(cols, week):
            with col:
                render_day(day, st.session_state.calendar_year, st.session_state.calendar_month, person, color, events)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Najbliższe dni poza biurem")
    future_events = [
        (iso, item)
        for iso, item in events.items()
        if datetime.fromisoformat(iso).date() >= today
    ]
    future_events = future_events[:12]

    if not future_events:
        st.info("Nie ma jeszcze żadnych przyszłych dni poza biurem.")
    else:
        for iso, item in future_events:
            txt_color = text_color_for_bg(item["color"])
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 14px; border:1px solid rgba(15,23,42,0.08); border-radius:16px; margin-bottom:8px; background:rgba(255,255,255,0.62);">
                    <div style="font-weight:900; color:#0f172a;">{polish_date_label(iso)}</div>
                    <div style="border-radius:999px; padding:7px 11px; font-weight:900; background:{item['color']}; color:{txt_color};">{item['person']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Legenda i zasady"):
        legend_html = "".join(
            f'<span class="legend-item"><span class="dot" style="background:{DEFAULT_COLORS[name]};"></span>{name}</span>'
            for name in PEOPLE
        )
        st.markdown(legend_html, unsafe_allow_html=True)
        st.write(
            "Każdy może zaznaczyć wolny dzień. Dzień zajęty przez inną osobę jest zablokowany. "
            "Odznaczyć dzień może tylko osoba, która go wcześniej zaznaczyła."
        )


if __name__ == "__main__":
    main()
