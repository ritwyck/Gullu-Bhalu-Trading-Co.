import streamlit as st

# Hide Streamlit default navigation (optional, if you use custom links)


def hide_default_nav():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)


# Custom CSS for sidebar navigation links
st.markdown("""
<style>
.sidebar-nav a.custom-link {
    color: #111 !important;             /* pure black */
    text-decoration: none !important;   /* no underline */
    font-size: 1.35rem !important;      /* bigger text */
    font-weight: 500 !important;
    display: block;
    padding: 7px 0 7px 6px;
    border-radius: 6px;
    margin-bottom: 2px;
    transition: background 0.2s, color 0.2s;
}
.sidebar-nav a.custom-link:hover {
    color: #222 !important;
    background: #e6e6e6;
    text-decoration: none !important;
}
.sidebar-nav .selected-link {
    color: #111 !important;
    font-size: 1.5rem !important;       /* even bigger, bold */
    font-weight: 700 !important;
    background: #eaeaea;
    padding: 8px 0 8px 6px;
    border-radius: 7px;
    box-shadow: none;
    margin-bottom: 2px;
}
</style>
""", unsafe_allow_html=True)


def custom_sidebar():
    st.sidebar.image("trade-jockey.png", width=120)
    st.sidebar.markdown("## Navigation")

    pages = ["All-Stocks", "Compare-Stocks", "Stocks"]
    params = st.query_params
    current_page = params.get("page", "Stocks")

    # Render navigation links
    links_html = "<div class='sidebar-nav'>\n"
    for page in pages:
        url = f"/?page={page}"
        if page == current_page:
            links_html += (
                f"<div class='selected-link'>{page}</div>\n"
            )
        else:
            # Force reload in same tab, styled as a custom link
            links_html += (
                f"<a class='custom-link' href='{url}' target='_self'>{page}</a>\n"
            )
    links_html += "</div>"
    st.sidebar.markdown(links_html, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by Trade Jockey*")
    return current_page
