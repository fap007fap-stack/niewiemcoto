import streamlit as st
from datetime import datetime
from auth import check_password, USERS
from database import init_db, get_bookings
from styles import apply_styles
from calendar_ui import render_calendar
from requests import show_notifications, swap_ui

st.set_page_config(page_title="OOO Calendar", layout="wide")

def main():
    init_db()
    apply_styles()

    if not check_password():
        st.stop()

    st.title("📅 OOO Calendar - Rezerwacja Dni")
    
    # Sidebar - Wybór użytkownika
    st.sidebar.title("Ustawienia")
    selected_user = st.sidebar.selectbox("Kim jesteś?", list(USERS.keys()))
    user_color = USERS[selected_user]
    
    st.sidebar.markdown(f"Twój kolor: <span style='color:{user_color}'>████</span>", unsafe_allow_html=True)
    
    # Powiadomienia
    show_notifications(selected_user)
    
    # Główny widok
    now = datetime.now()
    year = st.sidebar.number_input("Rok", min_value=2024, max_value=2030, value=now.year)
    month = st.sidebar.slider("Miesiąc", 1, 12, now.month)
    
    tab1, tab2 = st.tabs(["📅 Kalendarz", "🍩 Zamiana Dni"])
    
    with tab1:
        render_calendar(year, month, selected_user, user_color)
    
    with tab2:
        bookings = get_bookings()
        swap_ui(selected_user, bookings)

    # Stopka z odświeżaniem
    if st.button("🔄 Odśwież dane"):
        st.rerun()

if __name__ == "__main__":
    main()
