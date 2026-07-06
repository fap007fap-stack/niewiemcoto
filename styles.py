import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #262730;
            color: white;
            border: 1px solid #4B4B4B;
        }
        .stButton>button:hover {
            border: 1px solid #FF4B4B;
            color: #FF4B4B;
        }
        .calendar-day {
            border: 1px solid #333;
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            min-height: 80px;
        }
        .weekend {
            background-color: #1a1c24 !important;
            color: #555 !important;
        }
        .booked {
            font-weight: bold;
        }
        .notification-card {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #FF4B4B;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
