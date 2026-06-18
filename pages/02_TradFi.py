import streamlit as st
import plotly.express as px
import pandas as pd
from utils.tradfi_data import (
    get_rwa_stats,
    get_rwa_categories,
    get_top_rwa_assets,
    get_rwa_networks,
    get_tokenized_assets,
    get_rwa_tvl_trend
)

st.sidebar.title("W3Intelligence")
st.title("📈 TradFi & RWA Dashboard")

st.subheader("RWA Market Overview")
rwa_stats = get_rwa_stats()

if "error" not in rwa_stats:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Distributed Value", rwa_stats["distributed_value"])
    with col2:
        st.metric("Represented Value", rwa_stats["represented_value"])
    with col3:
        st.metric("Total Holders", rwa_stats["total_holders"])
    with col4:
        st.metric("Stablecoin Value", rwa_stats["stablecoin_value"])

st.markdown("---")

st.subheader("RWA Categories")
@st.cache_data(ttl=300)
def cached_get_rwa_categories():
    return get_rwa_categories()

categories = cached_get_rwa_categories()
if "error" not in categories:
    cat_df = pd.DataFrame([{
        "Category": c["name"],
        "Assets": c["asset_count"],
        "Total Value (M $)": c["total_value"]
    } for c in categories])
    fig_categories = px.pie(cat_df, values="Total Value (M $)", names="Category",
                            title="RWA Category Distribution")
    fig_categories.update_layout(template="plotly_dark")
    st.plotly_chart(fig_categories, use_container_width=True)
    st.dataframe(cat_df, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader("Top RWA Assets")
top_assets = get_top_rwa_assets(10)
if "error" not in top_assets:
    asset_df = pd.DataFrame([{
        "Symbol": a["symbol"],
        "Name": a["name"],
        "Category": a["category"],
        "Value": a["value_str"],
        "24h Change": a["change_24h"]
    } for a in top_assets])
    st.dataframe(asset_df, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader("RWA by Network")
networks = get_rwa_networks()
if "error" not in networks:
    network_df = pd.DataFrame([{
        "Rank": n["rank"],
        "Network": n["name"],
        "RWA Count": n["rwa_count"],
        "Value": n["value"],
        "Value (Str)": n["value_str"],
        "30D Change": n["change_30d"],
        "Market Share": n["market_share"]
    } for n in networks])
    fig_networks = px.bar(network_df, x="Network", y="Value", color="Market Share",
                          title="RWA Value by Network")
    fig_networks.update_layout(template="plotly_dark")
    st.plotly_chart(fig_networks, use_container_width=True)
    
    display_df = network_df[["Rank", "Network", "RWA Count", "Value (Str)", "30D Change", "Market Share"]]
    display_df.columns = ["Rank", "Network", "RWA Count", "Value", "30D Change", "Market Share"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader("RWA TVL Trend")
trend_data = get_rwa_tvl_trend()
fig_trend = px.line(trend_data, x="month", y="tvl", title="RWA TVL Growth")
fig_trend.update_layout(template="plotly_dark")
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

st.subheader("Tokenized Assets")
tokenized_assets = get_tokenized_assets()
asset_df = pd.DataFrame([{
    "Asset": a["name"],
    "Symbol": a["symbol"],
    "Issuer": a["issuer"],
    "Category": a.get("category", "N/A"),
    "Amount": a["amount"]
} for a in tokenized_assets])
st.dataframe(asset_df, use_container_width=True, hide_index=True)

