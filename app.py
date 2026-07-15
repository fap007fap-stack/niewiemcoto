import streamlit as st
import calendar
from streamlit_autorefresh import st_autorefresh
import json
import base64
import requests
import time
from datetime import date

st.set_page_config(layout="wide", page_title="Kalendarz Zespołu")

# --- KONFIGURACJA ---
def get_app_password():
    try:
        return st.secrets["APP_PASSWORD"]
    except Exception:
        st.error("❌ Brak APP_PASSWORD w secrets!")
        st.stop()


PASSWORD = get_app_password()
DEFAULT_USERS = {
    "Dagmara": "#ff5c8d",
    "Julia": "#b05cff",
    "Darek": "#4da6ff",
    "Szymon": "#45d483",
    "Michał": "#ffb347"
}
PL = ["", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
FILE = "calendar_data.json"
GITHUB_USER = "fap007fap-stack"
REPO = "niewiemcoto"
BRANCH = "main"

# --- OBSŁUGA GITHUB API Z BŁĘDAMI ---
def get_github_token():
    try:
        return st.secrets["GITHUB_TOKEN"]
    except Exception:
        st.error("❌ Brak GITHUB_TOKEN w secrets! Aplikacja nie może zapisywać danych.")
        st.stop()


TOKEN = get_github_token()


def github_api_call(method, url, payload=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10)
        elif method == "PUT":
            r = requests.put(url, headers=headers, json=payload, timeout=10)

        if r.status_code == 404:
            return None, None

        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.Timeout:
        return None, "Limit czasu połączenia z GitHub minął. Spróbuj ponownie."
    except requests.exceptions.ConnectionError:
        return None, "Błąd połączenia z internetem."
    except requests.exceptions.HTTPError:
        if r.status_code == 401:
            return None, "Błąd autoryzacji GitHub (zły token)."
        return None, f"Błąd GitHub API: {r.status_code}"
    except Exception as e:
        return None, f"Nieoczekiwany błąd: {str(e)}"


def github_load():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}?ref={BRANCH}"
    res, err = github_api_call("GET", url)

    if err:
        st.error(f"❌ Błąd ładowania: {err}")
        st.stop()

    if res is None:
        return {"_users": DEFAULT_USERS}, ""

    content = base64.b64decode(res["content"]).decode()
    data = json.loads(content)

    if "_users" not in data:
        data["_users"] = DEFAULT_USERS

    return data, res["sha"]


def github_get_sha():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}?ref={BRANCH}"
    res, err = github_api_call("GET", url)
    if err or res is None:
        return ""
    return res["sha"]


def github_save(data, sha):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}"
    encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()

    payload = {
        "message": "Update calendar and users",
        "content": encoded,
        "sha": sha,
        "branch": BRANCH
    }

    res, err = github_api_call("PUT", url, payload)
    if err:
        raise Exception(err)
    return res["content"]["sha"]


# --- STYLIZACJA ---
st.markdown("""
<style>
/* Paleta inspirowana Empikiem: musztarda, czerń i ciepła biel. */
:root {
    --empik-yellow: #e8b21d;
    --empik-yellow-light: #f6ca48;
    --empik-ink: #0b0b09;
    --empik-cream: #fff8e7;
    --empik-line: rgba(11, 11, 9, 0.22);
}

.stApp {
    background:
        radial-gradient(circle at 92% 6%, rgba(255, 248, 231, 0.30) 0 9%, transparent 30%),
        linear-gradient(135deg, #f4c33a 0%, var(--empik-yellow) 48%, #d99c0d 100%);
    color: var(--empik-ink);
}

[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1420px; padding-top: 2.5rem; padding-bottom: 3rem; }

h1, h2, h3, p, label, [data-testid="stWidgetLabel"] p {
    color: var(--empik-ink) !important;
}

[data-testid="stSidebar"] {
    background: rgba(11, 11, 9, 0.94);
    border-right: 1px solid rgba(255, 248, 231, 0.18);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--empik-cream) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="select"] > div {
    background: rgba(255, 248, 231, 0.88) !important;
    border-color: var(--empik-line) !important;
    color: var(--empik-ink) !important;
}

.stButton > button {
    width: 100%;
    min-height: 44px;
    background: rgba(11, 11, 9, 0.94);
    color: var(--empik-cream);
    border: 1px solid rgba(255, 248, 231, 0.30);
    border-radius: 10px;
    font-weight: 750;
    letter-spacing: 0.01em;
    box-shadow: 0 7px 15px rgba(57, 37, 0, 0.18);
    transition: transform 150ms ease, background 150ms ease, box-shadow 150ms ease;
}

.stButton > button,
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: var(--empik-cream) !important;
}

.stButton > button:hover {
    background: #20201a;
    border-color: var(--empik-cream);
    color: var(--empik-cream);
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(57, 37, 0, 0.26);
}

.user-accent {
    height: 8px;
    border-radius: 0 0 8px 8px;
    margin: -8px 7px 14px;
    box-shadow: 0 6px 12px rgba(57, 37, 0, 0.20);
}

.calendar-rule {
    height: 2px;
    margin: 12px 0 14px;
    background: linear-gradient(90deg, rgba(11, 11, 9, 0.75), rgba(11, 11, 9, 0.10));
}

.day-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 9px;
    padding: 9px 11px;
    background: rgba(11, 11, 9, 0.68);
    border: 1px solid rgba(255, 248, 231, 0.22);
    border-radius: 10px;
    color: var(--empik-cream);
    font-size: 20px;
    font-weight: 800;
    box-shadow: 0 8px 18px rgba(57, 37, 0, 0.16);
}

.today-badge {
    display: inline-flex;
    align-items: center;
    background: var(--empik-yellow-light);
    border: 1px solid rgba(255, 248, 231, 0.55);
    border-radius: 999px;
    color: var(--empik-ink);
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
}

.person-pill {
    color: white;
    padding: 8px 10px;
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 8px;
    font-weight: 700;
    margin-bottom: 6px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(57, 37, 0, 0.17);
}
</style>
""", unsafe_allow_html=True)

# --- LOGOWANIE ---
if "ok" not in st.session_state:
    st.session_state.ok = False

if not st.session_state.ok:
    st.title("🔒 Logowanie")
    p = st.text_input("Hasło", type="password")
    if st.button("Wejdź"):
        if p == PASSWORD:
            st.session_state.ok = True
            st.rerun()
        else:
            st.error("Błędne hasło")
    st.stop()

st_autorefresh(interval=30000, key="calendar_refresh")

# Ładowanie danych
data, sha = github_load()
USERS = data["_users"]

# Synchronizacja SHA
if "last_sha" not in st.session_state:
    st.session_state.last_sha = sha

current_sha = github_get_sha()
if current_sha and current_sha != st.session_state.last_sha:
    st.session_state.last_sha = current_sha
    st.rerun()

# --- SIDEBAR: EDYCJA UŻYTKOWNIKÓW ---
with st.sidebar:
    st.header("⚙️ Ustawienia")
    with st.expander("Edytuj nazwy użytkowników"):
        new_users = {}
        changed = False
        for old_name, color in USERS.items():
            new_name = st.text_input(f"Użytkownik ({color})", value=old_name, key=f"edit_{color}")
            new_users[new_name] = color
            if new_name != old_name:
                changed = True

        if changed and st.button("Zapisz nowe nazwy"):
            new_data = {"_users": new_users}
            name_map = {old: new for old, new in zip(USERS.keys(), new_users.keys())}

            for key, people in data.items():
                if key == "_users":
                    continue
                new_data[key] = [name_map.get(person, person) for person in people]

            try:
                new_sha = github_save(new_data, st.session_state.last_sha)
                st.session_state.last_sha = new_sha
                st.success("Nazwy zaktualizowane!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Błąd zapisu nazw: {e}")

# --- GŁÓWNY INTERFEJS ---
t = date.today()
a, b = st.columns([1, 1])
with a:
    y = st.number_input("Rok", value=t.year, step=1)
with b:
    m = st.selectbox("Miesiąc", range(1, 13), index=t.month - 1, format_func=lambda x: PL[x])

if "me" not in st.session_state or st.session_state.me not in USERS:
    st.session_state.me = list(USERS.keys())[0]

me = st.session_state.me
st.title(f"{PL[m]} {y}")

cols = st.columns(len(USERS))
for i, (user, color) in enumerate(USERS.items()):
    active = user == me
    border = "4px solid white" if active else "1px solid #222"
    if cols[i].button(user, key="user" + user, use_container_width=True):
        st.session_state.me = user
        st.rerun()
    cols[i].markdown(f"""
        <div class="user-accent" style="background:{color}; border:{border};"></div>
    """, unsafe_allow_html=True)

# Widok tygodnia roboczego: poniedziałek–piątek
heads = ["Tydzień", "Pon", "Wt", "Śr", "Czw", "Pt"]
cols = st.columns(len(heads))
for column, header in zip(cols, heads):
    column.markdown(f"**{header}**")

st.markdown('<div class="calendar-rule"></div>', unsafe_allow_html=True)

cal = calendar.Calendar(firstweekday=0)
for week in cal.monthdatescalendar(y, m):
    workdays = week[:5]

    # Pomija wiersz, gdy w danym tygodniu wypada tylko weekend z wybranego miesiąca.
    if not any(day.month == m for day in workdays):
        continue

    cols = st.columns(len(heads))
    cols[0].markdown(f"### W{workdays[0].isocalendar()[1]}")

    for i, day in enumerate(workdays):
        if day.month != m:
            cols[i + 1].write("")
            continue

        key = str(day)
        people = data.get(key, [])
        if isinstance(people, str):
            people = [people]

        with cols[i + 1]:
            today_badge = '<span class="today-badge">📍 Dzisiaj</span>' if day == t else ""
            st.markdown(
                f'<div class="day-heading">{day.day}{today_badge}</div>',
                unsafe_allow_html=True,
            )

            for idx, person in enumerate(people):
                if person not in USERS:
                    continue

                color = USERS[person]
                c1, c2 = st.columns([4, 1], gap=None)
                with c1:
                    st.markdown(f"""
                        <div class="person-pill" style="background:linear-gradient(135deg, {color}, {color}bd);">
                        {person}
                        </div>
                    """, unsafe_allow_html=True)

                with c2:
                    if person == me and st.button("✕", key=f"del{key}{idx}", use_container_width=True):
                        try:
                            latest_data, latest_sha = github_load()
                            person_list = latest_data.get(key, [])
                            if person in person_list:
                                person_list.remove(person)
                            if person_list:
                                latest_data[key] = person_list
                            else:
                                latest_data.pop(key, None)

                            new_sha = github_save(latest_data, latest_sha)
                            st.session_state.last_sha = new_sha
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd usuwania: {e}")

            if me not in people and len(people) < 2:
                if st.button("➕ Dodaj", key="add" + key, use_container_width=True):
                    try:
                        latest_data, latest_sha = github_load()
                        person_list = latest_data.get(key, [])
                        if me not in person_list and len(person_list) < 2:
                            person_list.append(me)
                            latest_data[key] = person_list
                            new_sha = github_save(latest_data, latest_sha)
                            st.session_state.last_sha = new_sha
                            time.sleep(0.5)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Błąd dodawania: {e}")
