import streamlit as st, calendar, json, os
from datetime import date
st.set_page_config(layout="wide",page_title="Kalendarz Zespołu")
PASSWORD="dexflex67"
USERS={"Dagmara":"#ff5c8d","Julia":"#b05cff","Darek":"#4da6ff","Szymon":"#45d483","Michał":"#ffb347"}
PL=["","Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec","Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]
FILE="calendar_data.json"

st.markdown("""<style>
.block{border-radius:12px;padding:8px;height:120px;border:1px solid #ddd;background:#fafafa}
</style>""",unsafe_allow_html=True)
if "ok" not in st.session_state: st.session_state.ok=False
if not st.session_state.ok:
    st.title("🔒 Logowanie")
    p=st.text_input("Hasło",type="password")
    if st.button("Wejdź"):
        if p==PASSWORD:
            st.session_state.ok=True; st.rerun()
        else: st.error("Błędne hasło")
    st.stop()

data={}
if os.path.exists(FILE): data=json.load(open(FILE,encoding="utf8"))

t=date.today()
a,b,c=st.columns([1,1,2])
with a: y=st.number_input("Rok",value=t.year,step=1)
with b: m=st.selectbox("Miesiąc",range(1,13),index=t.month-1,format_func=lambda x:PL[x])
with c: me=st.selectbox("Jesteś",list(USERS))
st.title(f"{PL[m]} {y}")

legend=st.columns(len(USERS))
for col,(u,colr) in zip(legend,USERS.items()):
    col.markdown(f"<div style='background:{colr};color:white;padding:6px;border-radius:8px;text-align:center'>{u}</div>",unsafe_allow_html=True)

heads=["Week","Pon","Wt","Śr","Czw","Pt","Sob","Nd"]
cols=st.columns(8)
for c,h in zip(cols,heads): c.markdown(f"**{h}**")

cal=calendar.Calendar(firstweekday=0)
for week in cal.monthdatescalendar(y,m):
    cols=st.columns(8)
    cols[0].write("W"+str(week[0].isocalendar()[1]))
    for i,d in enumerate(week):
        if d.month!=m:
            cols[i+1].write("")
            continue
        key=str(d)
        people=data.get(key,[])
        with cols[i+1]:
            st.markdown(f"**{d.day}**")
            for idx,p in enumerate(people):
                cc=USERS[p]
                c1,c2=st.columns([5,1])
                c1.markdown(f"<div style='background:{cc};color:white;padding:2px 6px;border-radius:6px'>{p}</div>",unsafe_allow_html=True)
                if p==me:
                    if c2.button("❌",key=f"del{key}{idx}"):
                        people.remove(p)
                        if people: data[key]=people
                        else: data.pop(key,None)
                        json.dump(data,open(FILE,"w",encoding="utf8"),ensure_ascii=False)
                        st.rerun()
            if me not in people and len(people)<2:
                if st.button("➕",key="add"+key):
                    people.append(me)
                    data[key]=people
                    json.dump(data,open(FILE,"w",encoding="utf8"),ensure_ascii=False)
                    st.rerun()
            elif len(people)>=2:
                st.caption("Pełny")
