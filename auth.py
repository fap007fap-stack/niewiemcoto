import streamlit as st

def check_password():
    """Zwraca True, jeśli hasło jest poprawne."""
    def password_entered():
        if st.session_state["password"] == "dexflex67":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Hasło", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Hasło", type="password", on_change=password_entered, key="password")
        st.error("Błędne hasło")
        return False
    else:
        return True

USERS = {
    "Michał": "#FF4B4B",
    "Dagmara": "#4BFF4B",
    "Julka": "#4B4BFF",
    "Szymon": "#FFFF4B",
    "Darek": "#FF4BFF"
}
