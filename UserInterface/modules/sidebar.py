import streamlit as st


def custom_sidebar():
    st.sidebar.image("trade-jockey.png", width=120)
    st.sidebar.markdown("## Navigation")
    pages = ["Home", "All-Stocks", "Compare-Stocks", "Stocks"]
    params = st.query_params
    current_page = params.get("page", "Home")

    for page in pages:
        url = f"/?page={page}"
    if page == current_page:
        st.sidebar.markdown(
            f"- <strong>{page}</strong>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            f'- <a href="{url}">{page}</a>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by Trade Jockey*")
    return current_page


def hide_default_nav():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
