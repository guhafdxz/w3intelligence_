import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.crypto_data import (
    get_bitcoin_price,
    get_ethereum_price,
    get_fear_greed_index,
    get_cmc_hot_tokens,
    get_vix_data,
    get_bitcoin_etf_flows,
    get_contract_open_interest,
    get_crypto_correlation_data,
    get_global_market_metrics,
    get_dominance_metrics
)

st.sidebar.title("W3Intelligence")
st.title("💰 Crypto Dashboard")

col1, col2, col3 = st.columns(3)

btc_data = get_bitcoin_price()
if "error" not in btc_data:
    with col1:
        st.metric("BTC", f"${int(btc_data['usd'])}", f"{btc_data['usd_24h_change']:.2f}%")

eth_data = get_ethereum_price()
if "error" not in eth_data:
    with col2:
        st.metric("ETH", f"${int(eth_data['usd'])}", f"{eth_data['usd_24h_change']:.2f}%")

market_metrics = get_global_market_metrics()
if "error" not in market_metrics:
    with col3:
        market_cap_t = market_metrics["total_market_cap"] / 1e12
        st.metric("Market Cap", f"${market_cap_t:.1f}T")

col4, col5, col6 = st.columns(3)

dominance = get_dominance_metrics()
if "error" not in dominance:
    with col4:
        btc_dom = dominance["btc_dominance"]
        btc_change = dominance["btc_24h_change"]
        st.metric("BTC Dominance", f"{btc_dom:.1f}%", f"{btc_change:+.2f}%")
    
    with col5:
        eth_dom = dominance["eth_dominance"]
        eth_change = dominance["eth_24h_change"]
        st.metric("ETH Dominance", f"{eth_dom:.1f}%", f"{eth_change:+.2f}%")

fg_index = get_fear_greed_index()
if "error" not in fg_index:
    with col6:
        st.metric("Fear & Greed", fg_index["value"], fg_index["classification"])

st.markdown("---")

st.subheader("Bitcoin ETF Flows")
etf_data = get_bitcoin_etf_flows()
if isinstance(etf_data, dict) and "overview" in etf_data and "detail" in etf_data:
    overview = etf_data["overview"]
    detail = etf_data["detail"]
    
    if "data" in overview and "total" in overview["data"]:
        total_flow = overview["data"]["total"]
        flow_million = total_flow / 1e6
        st.metric("24h Net Flow", f"${flow_million:,.2f}M")
    
    if "data" in overview and "points" in overview["data"]:
        points = overview["data"]["points"]
        if isinstance(points, list) and len(points) > 0 and isinstance(points[0], dict):
            dates = []
            values = []
            for point in points:
                if "timestamp" in point and "value" in point:
                    timestamp = int(point["timestamp"])
                    value = int(point["value"])
                    dates.append(datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d"))
                    values.append(value / 1e6)
            
            fig_etf = px.line(x=dates, y=values, title="BTC ETF Net Flow (Daily)", labels={"x": "Date", "y": "Net Flow (M $)"})
            fig_etf.update_layout(template="plotly_dark")
            st.plotly_chart(fig_etf, use_container_width=True)
    
    etf_full_names = etf_data.get("etf_full_names", {})
    if "data" in detail and "points" in detail["data"]:
        detail_points = detail["data"]["points"]
        if isinstance(detail_points, list) and len(detail_points) > 0:
            etf_details = []
            for point in detail_points:
                if isinstance(point, dict):
                    etf_symbol = point.get("name", "")
                    etf_full_name = etf_full_names.get(etf_symbol, etf_symbol)
                    data_points = point.get("data", [])
                    total_flow = 0
                    for dp in data_points:
                        if isinstance(dp, dict) and "value" in dp:
                            total_flow += int(dp["value"])
                    
                    etf_details.append({
                        "ETF": etf_symbol,
                        "Full Name": etf_full_name,
                        "24h Net Flow": f"${total_flow / 1e6:,.2f}M"
                    })
            
            if etf_details:
                st.subheader("Individual ETF Net Flow")
                st.dataframe(pd.DataFrame(etf_details), use_container_width=True, hide_index=True)
else:
    st.write("Failed to fetch ETF data")

st.markdown("---")

st.subheader("Futures Open Interest (BTC)")
st.components.v1.iframe(
    "https://charts.checkonchain.com/btconchain/derivatives/derivatives_futures_oi_byexchange_1/derivatives_futures_oi_byexchange_1_light.html",
    width=None,
    height=500,
    scrolling=False
)

st.markdown("---")

st.subheader("BTC Correlation with Traditional Assets")
corr_data = get_crypto_correlation_data()
fig_corr = px.bar(corr_data, x="asset", y="correlation", color="correlation",
                  color_continuous_scale="RdBu", range_color=[-1, 1])
fig_corr.update_layout(template="plotly_dark")
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

st.subheader("VIX Index (30-day)")
vix_data = get_vix_data()
if "error" not in vix_data:
    fig_vix = px.line(vix_data, x="date", y="VIX", title="VIX Volatility Index")
    fig_vix.update_layout(template="plotly_dark")
    st.plotly_chart(fig_vix, use_container_width=True)

st.markdown("---")

st.subheader("Top Tokens by Market Cap")
hot_tokens = get_cmc_hot_tokens()
if "error" not in hot_tokens:
    # Filter out tokens with specific symbols (Index DTF, etc.)
    exclude_symbols = ["CMC20", "CMC200", "DTF", "TOP", "TOP20"]
    filtered_tokens = [t for t in hot_tokens if t["symbol"] not in exclude_symbols]
    
    token_df = [{
        "Name": t["name"],
        "Symbol": t["symbol"],
        "Price": f"${t['price']:,.2f}",
        "24h Change": f"{t['change_24h']:.2f}%",
        "Market Cap": f"${t['market_cap']/1e9:,.2f}B"
    } for t in filtered_tokens]
    st.dataframe(pd.DataFrame(token_df), use_container_width=True, hide_index=True)