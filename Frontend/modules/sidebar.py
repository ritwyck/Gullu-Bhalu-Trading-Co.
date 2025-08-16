import streamlit as st


def custom_sidebar():
    st.sidebar.image("trade-jockey.png", width=120)
    params = st.query_params
    page = params.get('page', 'Home')
    for p in ["Home", "All-Stocks", "Compare-Stocks", "Stocks"]:
        url = f"/?page={p.replace(' ', '%20')}"
        if page == p:
            st.sidebar.markdown(
                f"- <span style='font-weight:bold;color:#04B4D9'>{p}</span>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown(
                f"- <a href='{url}'>{p}</a>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by Trade Jockey*")
    return page


def hide_default_nav():
    """Hide Streamlit's default multipage sidebar navigation."""
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
