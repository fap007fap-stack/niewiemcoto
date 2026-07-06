import streamlit as st

PASSWORD = "dexflex67"

def login():

    if st.session_state.get("logged", False):
        return True

    st.markdown("## 🔐 Logowanie")

    password = st.text_input(
        "Hasło",
        type="password"
    )

    if st.button("Wejdź", use_container_width=True):

        if password == PASSWORD:
            st.session_state.logged = True
            st.rerun()

        st.error("Niepoprawne hasło")

    return False
