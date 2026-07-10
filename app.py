import streamlit as st
import calendar
import json
import base64
import requests
from datetime import date
st.set_page_config(layout="wide",page_title="Kalendarz Zespołu")
PASSWORD="dexflex67"
USERS={"Dagmara":"#ff5c8d","Julia":"#b05cff","Darek":"#4da6ff","Szymon":"#45d483","Michał":"#ffb347"}
PL=["","Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec","Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]
FILE="calendar_data.json"
GITHUB_USER = "fap007fap-stack"
REPO = "niewiemcoto"
BRANCH = "main"

TOKEN = st.secrets["GITHUB_TOKEN"]
@st.cache_data(ttl=2)
def github_load():

    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}?ref={BRANCH}"

    r = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json"
        }
    )

    r.raise_for_status()

    j = r.json()

    content = base64.b64decode(j["content"]).decode()

    return json.loads(content), j["sha"]


def github_save(data, sha):

    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}"

    encoded = base64.b64encode(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode()
    ).decode()

    payload = {
        "message": "Update calendar",
        "content": encoded,
        "sha": sha,
        "branch": BRANCH
    }

    r = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        json=payload
    )

    r.raise_for_status()

    return r.json()["content"]["sha"]
st.markdown("""
<style>

.stButton>button{
    width:100%;
    border-radius:12px;
}

.day-card{
    background:#1c2333;
    border:1px solid #3b4458;
    border-radius:14px;
    padding:8px;
    min-height:165px;
    margin-bottom:6px;
}

.day-card:hover{
    border:1px solid #60a5fa;
}

.user-pill{
    border-radius:8px;
    color:white;
    padding:5px 8px;
    margin-top:4px;
    margin-bottom:4px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    font-size:14px;
    font-weight:600;
}

.day-number{
    font-size:20px;
    font-weight:bold;
    margin-bottom:8px;
}

.weekend{
    background:#242936;
}

.today{
    border:2px solid #4ea1ff;
}

.user-select button{
    height:55px;
    border-radius:14px;
    font-weight:bold;
}

</style>
""",unsafe_allow_html=True)
if "ok" not in st.session_state: st.session_state.ok=False
if not st.session_state.ok:
    st.title("🔒 Logowanie")
    p=st.text_input("Hasło",type="password")
    if st.button("Wejdź"):
        if p==PASSWORD:
            st.session_state.ok=True; st.rerun()
        else: st.error("Błędne hasło")
    st.stop()

data, sha = github_load()

t=date.today()
a,b=st.columns([1,1])

with a:
    y=st.number_input(
        "Rok",
        value=t.year,
        step=1
    )

with b:
    m=st.selectbox(
        "Miesiąc",
        range(1,13),
        index=t.month-1,
        format_func=lambda x:PL[x]
    )

if "me" not in st.session_state:
    st.session_state.me="Dagmara"

me=st.session_state.me
st.title(f"{PL[m]} {y}")

cols = st.columns(len(USERS))

for i,(u,colr) in enumerate(USERS.items()):

    active=u==me

    border="4px solid white" if active else "1px solid #222"

    if cols[i].button(
        u,
        key="user"+u,
        use_container_width=True
    ):
        st.session_state.me=u
        st.rerun()

    cols[i].markdown(f"""
    <div style="
        height:10px;
        background:{colr};
        border-radius:0 0 8px 8px;
        margin-top:-8px;
        border:{border};
    "></div>
    """,unsafe_allow_html=True)
    

heads=["Week","Pon","Wt","Śr","Czw","Pt","Sob","Nd"]
cols=st.columns(8)
for c,h in zip(cols,heads): c.markdown(f"**{h}**")

cal = calendar.Calendar(firstweekday=0)

for week in cal.monthdatescalendar(y, m):

    cols = st.columns(8)

    cols[0].markdown(
        f"### W{week[0].isocalendar()[1]}"
    )

    for i, d in enumerate(week):

        if d.month != m:
            cols[i+1].write("")
            continue

        key = str(d)

        people = data.get(key, [])

        # kompatybilność ze starym json
        if isinstance(people, str):
            people = [people]
            data[key] = people

        with cols[i+1]:

            st.markdown(f"### {d.day}")

            # ---------- wpisy ----------
            for idx, person in enumerate(people):

                color = USERS[person]

                c1, c2 = st.columns([6,1], gap="small")

                with c1:

                    st.markdown(
                        f"""
                        <div style="
                            background:{color};
                            color:white;
                            padding:7px 10px;
                            border-radius:8px;
                            font-weight:600;
                            margin-bottom:6px;
                            text-align:center;
                        ">
                        {person}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c2:

                    if person == me:

                        if st.button(
                            "✕",
                            key=f"del{key}{idx}",
                            use_container_width=True
                        ):

                            latest_data, sha = github_load()

                            people = latest_data.get(key, [])

                            if person in people:
                                people.remove(person)
                            
                            if people:
                                latest_data[key] = people
                            else:
                                latest_data.pop(key, None)
                            
                            try:
                                sha = github_save(latest_data, sha)
                                st.rerun()

                            except requests.HTTPError:
                                st.warning("⚠️ Ktoś właśnie zmienił kalendarz. Spróbuj ponownie.")

            # ---------- dodawanie ----------

            if me not in people:

                if len(people) < 2:

                    if st.button(
                        "➕ Dodaj",
                        key="add"+key,
                        use_container_width=True
                    ):

                        latest_data, sha = github_load()

                        people = latest_data.get(key, [])

                        if me not in people and len(people) < 2:
                            people.append(me)

                        latest_data[key] = people

                        try:
                            sha = github_save(latest_data, sha)
                            st.rerun()
                        
                        except requests.HTTPError:
                            st.warning("⚠️ Ktoś właśnie zmienił kalendarz. Spróbuj ponownie.")

                else:

                    st.error("Pełny")
