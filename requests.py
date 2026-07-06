import streamlit as st
from database import get_swap_requests, update_swap_status, create_swap_request, get_bookings

def show_notifications(user):
    st.sidebar.markdown("### 🍩 Powiadomienia")
    reqs = get_swap_requests(user)
    
    if reqs.empty:
        st.sidebar.info("Brak nowych próśb")
    
    for _, row in reqs.iterrows():
        with st.sidebar.container():
            st.markdown(f"""
                <div class="notification-card">
                    <b>{row['requester']}</b> chce zamienić:<br>
                    📅 {row['requested_date']} ↔️ {row['target_date']}
                </div>
            """, unsafe_allow_html=True)
            col1, col2 = st.sidebar.columns(2)
            if col1.button("✅ Akceptuj", key=f"acc-{row['id']}"):
                update_swap_status(row['id'], 'accepted')
                st.rerun()
            if col2.button("❌ Odrzuć", key=f"rej-{row['id']}"):
                update_swap_status(row['id'], 'rejected')
                st.rerun()

def swap_ui(user, bookings):
    st.subheader("🍩 Poproś o zamianę")
    
    my_bookings = bookings[bookings['user'] == user]
    others_bookings = bookings[bookings['user'] != user]
    
    if my_bookings.empty or others_bookings.empty:
        st.warning("Musisz mieć rezerwację i ktoś inny musi mieć rezerwację, aby dokonać zamiany.")
        return

    col1, col2 = st.columns(2)
    my_date = col1.selectbox("Twój dzień", my_bookings['date'])
    target_booking = col2.selectbox("Dzień do zamiany", others_bookings['date'])
    
    target_user = others_bookings[others_bookings['date'] == target_booking]['user'].values[0]
    
    if st.button("Wyślij prośbę o zamianę"):
        create_swap_request(user, target_user, my_date, target_booking)
        st.success(f"Wysłano prośbę do {target_user}!")
