
import streamlit as st
import json
from datetime import datetime, timedelta

DATA_FILE = 'bookings.json'

def load_bookings():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bookings(bookings):
    with open(DATA_FILE, 'w') as f:
        json.dump(bookings, f, indent=4)

def app():
    st.title('Aplikacja Kalendarza Rezerwacji')

    bookings = load_bookings()

    st.header('Zarezerwuj termin')
    selected_date = st.date_input('Wybierz datę', datetime.now())
    selected_time = st.time_input('Wybierz godzinę', datetime.now().time())
    name = st.text_input('Twoje imię')

    if st.button('Zarezerwuj'):
        date_str = selected_date.strftime('%Y-%m-%d')
        time_str = selected_time.strftime('%H:%M')
        datetime_str = f'{date_str} {time_str}'

        if date_str not in bookings:
            bookings[date_str] = []

        # Check for conflicts
        conflict = False
        for booking in bookings[date_str]:
            if booking['time'] == time_str:
                conflict = True
                break

        if conflict:
            st.error('Ten termin jest już zajęty. Wybierz inny.')
        else:
            bookings[date_str].append({'time': time_str, 'name': name})
            save_bookings(bookings)
            st.success(f'Termin {datetime_str} zarezerwowany dla {name}!')

    st.header('Istniejące rezerwacje')
    if bookings:
        for date_str, daily_bookings in sorted(bookings.items()):
            st.subheader(date_str)
            for booking in daily_bookings:
                st.write(f"- {booking['time']} - {booking['name']}")
    else:
        st.info('Brak rezerwacji.')

if __name__ == '__main__':
    app()
