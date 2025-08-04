import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Market & Peer Analysis", layout="wide")

# Sidebar - Company Selection
st.sidebar.title("Company & Sector Selection")
ticker_input = st.sidebar.text_input("Enter NSE Ticker (e.g., RELIANCE.NS)", "RELIANCE.NS")

# Optionally, map sectors to peer tickers (JSON or dict)
sector_peers = {
    "Oil & Gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    # Add more if desired
}

# Main Title
st.title("Market & Peer Analysis Dashboard (India)")

def fetch_info(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info
    except Exception as e:
        return {}

def plot_peers_metrics(tickers, metric):
    data = []
    names = []
    for t in tickers:
        info = fetch_info(t)
        val = info.get(metric, None)
        if val is not None:
            data.append(val)
            names.append(info.get("shortName", t))
    fig = go.Figure([go.Bar(x=names, y=data)])
    fig.update_layout(title=f"{metric} Comparison", xaxis_title="Company", yaxis_title=metric)
    st.plotly_chart(fig, use_container_width=True)

def get_news(company):
    url = f"https://news.google.com/search?q={company}+stock"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    headlines = [a.text for a in soup.find_all('a', class_='DY5T1d')[:5]]
    return headlines

if ticker_input:
    info = fetch_info(ticker_input)
    st.subheader(info.get('longName', ticker_input))

    col1, col2, col3 = st.columns(3)
    col1.write(f"**Sector:** {info.get('sector', 'N/A')}")
    col2.write(f"**Market Cap:** {info.get('marketCap', 'N/A')}")
    col3.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")

    st.markdown("---")
    st.subheader(":bar_chart: Peer Benchmarking")
    sector = info.get("sector", None)
    if sector in sector_peers:
        selected_peers = sector_peers[sector]
        plot_peers_metrics(selected_peers, "marketCap")
        plot_peers_metrics(selected_peers, "trailingPE")
    else:
        st.write("Peers unavailable for this sector. Edit 'sector_peers' for more.")

    st.markdown("---")
    st.subheader(":newspaper: Recent News")
    headlines = get_news(info.get('shortName', ''))
    for n in headlines:
        st.write("- " + n)

    # Stock price visualization
    st.markdown("---")
    st.subheader(":chart_with_upwards_trend: Stock Price Trend")
    price_his = yf.download(ticker_input, period="6mo")
    st.line_chart(price_his['Close'])

    # Export suggestion (user can screenshot or export data via download button)
else:
    st.write("Enter a valid NSE ticker to start!")
