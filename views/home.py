import streamlit as st


def render_home():
    st.markdown("<h1 style='color:#04B4D9;'>Welcome to Trade Jockey Dashboard</h1>",
                unsafe_allow_html=True)
    st.write("Use the sidebar to explore different analytics.")
