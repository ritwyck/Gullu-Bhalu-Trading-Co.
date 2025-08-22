import streamlit as st


def custom_sidebar():
    st.sidebar.image("trade-jockey.png", width=120)
    st.sidebar.markdown("## Navigation")

    pages = ["All-Stocks", "Compare-Stocks", "Stocks"]
    params = st.query_params
    current_page = params.get("page", "Stocks")

    for page in pages:
        url = f"/?page={page}"
        if page == current_page:
            st.sidebar.markdown(
                f"- <span style='color:#04B4D9;font-weight:bold'>{page}</span>",
                unsafe_allow_html=True
            )
        else:
            # force reload in same tab
            st.sidebar.markdown(
                f"- <a href='{url}' target='_self'>{page}</a>",
                unsafe_allow_html=True
            )

    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by Trade Jockey*")
    return current_page


def hide_default_nav():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
