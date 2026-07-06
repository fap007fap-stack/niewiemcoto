# app.py
import streamlit as st

st.set_page_config(page_title="Poza biurem", page_icon="📅", layout="wide")

st.markdown("""
<style>
.stApp{
    background:#0f1117;
    color:white;
}
.block-container{padding-top:1rem;max-width:1200px;}
.day{
    border-radius:10px;
    padding:10px;
    margin:4px;
    text-align:center;
    background:#1c1f26;
}
.weekend{
    background:#2d3138;
    color:#8f949c;
}
.req{
    background:#1b2638;
    border-left:4px solid #5aa9ff;
    padding:10px;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth=False

if not st.session_state.auth:
    pwd=st.text_input("Hasło",type="password")
    if st.button("Wejdź"):
        if pwd=="dexflex67":
            st.session_state.auth=True
            st.rerun()
        else:
            st.error("Niepoprawne hasło.")
    st.stop()

st.title("🏢 Kalendarz poza biurem")

st.info("Wersja demonstracyjna UI nowych funkcji.")

left,right=st.columns([1,2])

with left:
    person=st.selectbox("Osoba",["Dagmara","Szymon","Michał","Darek","Julka"])
    color=st.color_picker("Twój kolor","#4CAF50")

with right:
    st.subheader("Przykładowy kalendarz")
    cols=st.columns(7)
    days=["Pn","Wt","Śr","Cz","Pt","Sb","Nd"]
    for c,d in zip(cols,days):
        c.markdown(f"**{d}**")
    for week in range(5):
        cols=st.columns(7)
        for i,c in enumerate(cols):
            num=week*7+i+1
            weekend=i>=5
            klass="weekend" if weekend else "day"
            c.markdown(f'<div class="{klass}">{num}</div>',unsafe_allow_html=True)

st.divider()
st.subheader("🔒 Zajęty dzień")

st.warning("12 lipca jest już zajęty przez **Dagmarę**.")

if st.button("🍩 Poproś Dagmarę o możliwość zamiany (za coś słodkiego 😄)"):
    st.success("Prośba została wysłana do Dagmary.")

st.markdown('<div class="req"><b>Powiadomienie u Dagmary</b><br>Michał chce przejąć Twój dzień 12 lipca 🍩</div>',unsafe_allow_html=True)

c1,c2=st.columns(2)
with c1:
    if st.button("✅ Zgadzam się"):
        st.success("Zamiana zaakceptowana. Dzień zostaje przeniesiony.")
with c2:
    if st.button("❌ Odrzuć"):
        st.error("Prośba została odrzucona.")

st.caption("W finalnej wersji te akcje powinny być zapisane w bazie danych (SQLite/PostgreSQL), aby powiadomienia i zamiany działały między wszystkimi użytkownikami.")
