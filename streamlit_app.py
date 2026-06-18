import streamlit as st

st.set_page_config(
    page_title="W3Intelligence - Web3 Smart Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 W3Intelligence")
st.sidebar.title("W3Intelligence")
st.markdown("""
Welcome to W3Intelligence, your comprehensive Web3 intelligence platform.

**Navigate through the pages:**
- **Crypto** - Bitcoin/ETH fund flows, ETF data, open interest, correlations, VIX, Fear & Greed Index
- **TradFi** - Tokenized assets, RWA statistics, exchange listings
- **Premarket** - Prediction market insights
- **Tools** - LLM-powered chat and prediction topic analysis

**Key Features:**
- Real-time market data
- AI-powered analysis
- Interactive charts
- Multi-page navigation
""")

st.sidebar.success("Select a page from above")