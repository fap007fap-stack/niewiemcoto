import streamlit as st

from auth import login
from styles import css

st.set_page_config(
    page_title="Poza biurem",
    page_icon="🏢",
    layout="wide"
)

st.markdown(css, unsafe_allow_html=True)

if not login():
    st.stop()

st.title("🏢 Poza biurem")

users = [
    "Dagmara",
    "Szymon",
    "Michał",
    "Darek",
    "Julka"
]

left,right=st.columns([1,3])

with left:

    person=st.selectbox(
        "Osoba",
        users
    )

    color=st.color_picker(
        "Kolor",
        "#4CAF50"
    )

    st.success(
        f"Zalogowano jako {person}"
    )

with right:

    st.info(
        "W następnej części pojawi się pełny kalendarz."
    )
