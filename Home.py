
import streamlit as st


def main():
    st.set_page_config(
        page_title="Trade Jockey",
        page_icon="📈",
        layout="wide"
    )

    st.title("Trade Jockey")
    st.markdown(
        """
        Welcome to the Trade Jockey Dashboard.  
        Use the sidebar to navigate through different analyses and views of the market data.
        
        ---
        ### Available Pages
        - **Single Stock View:** Analyze one stock's volatility, ADX, and ratio metrics.
        - **Multi Stock View:** Compare multiple stocks side-by-side.
        - **All Stocks Overview:** Get a comprehensive view of all stocks with selection capability.
        
        ---
        **How to use:**  
        Select a page from the sidebar on the left to get started.
        """
    )

    st.markdown(
        """
        ### About  
        This trading dashboard provides deep insights into stock volatility and momentum indicators, helping you make informed trading decisions.  
        Data is refreshed daily from historical CSV files stored locally.
        """
    )


if __name__ == "__main__":
    main()
