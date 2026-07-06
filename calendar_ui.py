import streamlit as st
import calendar
from datetime import datetime, date
import pandas as pd
from database import get_bookings, add_booking, delete_booking

def render_calendar(year, month, selected_user, user_color):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.subheader(f"{month_name} {year}")
    
    bookings = get_bookings()
    
    # Nagłówki dni tygodnia
    cols = st.columns(7)
    days = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
                continue
            
            current_date = date(year, month, day)
            date_str = current_date.strftime("%Y-%m-%d")
            is_weekend = i >= 5
            
            # Sprawdź czy dzień jest zajęty
            booking = bookings[bookings['date'] == date_str]
            
            tile_style = "weekend" if is_weekend else ""
            
            with cols[i]:
                if not booking.empty:
                    user = booking.iloc[0]['user']
                    color = booking.iloc[0]['color']
                    st.markdown(f"""
                        <div style="background-color: {color}; color: black; padding: 5px; border-radius: 3px; text-align: center; font-size: 0.8em;">
                            {day}<br><b>{user}</b>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("❌", key=f"del-{date_str}"):
                        if user == selected_user:
                            delete_booking(date_str)
                            st.rerun()
                        else:
                            st.error("Nie możesz usunąć cudzej rezerwacji!")
                else:
                    st.markdown(f"""
                        <div style="text-align: center; color: {'#555' if is_weekend else '#fff'};">
                            {day}
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("➕", key=f"add-{date_str}"):
                        if add_booking(selected_user, date_str, user_color):
                            st.rerun()
                        else:
                            st.error("Dzień już zajęty!")
