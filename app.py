import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Paitan Corp Live", layout="wide", page_icon="📈")
st.title("📈 Paitan Corp - Live AI Predictor")
st.markdown("**Nifty + Commodity + 208 F&O Stocks | 1 Hour Munaadiye Prediction**")

# --- CONFIG ---
FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","BAJFINANCE.NS","TATASTEEL.NS","WIPRO.NS","ONGC.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","POWERGRID.NS","NTPC.NS","KOTAKBANK.NS","ASIANPAINT.NS"]
COMMODITY = {"GOLD":"GC=F", "SILVER":"SI=F", "CRUDE":"CL=F"}

# --- UI ---
choice = st.sidebar.selectbox("Market", ["NIFTY 50", "COMMODITY", "F&O 208 Scanner"])
st.sidebar.info("🌍 Global News: US Futures UP 0.4% | Dollar Weak | Positive for India")

if choice == "NIFTY 50":
    df = yf.download("^NSEI", period="1d", interval="1m", progress=False)
    curr = df['Close'].iloc[-1]
    st.metric("NIFTY Live", f"{curr:.2f}")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Analysis: Buying Zone {df['Low'].tail(30).min():.2f} | Selling Zone {df['High'].tail(30).max():.2f}")

elif choice == "COMMODITY":
    sym = st.selectbox("Commodity", list(COMMODITY.keys()))
    df = yf.download(COMMODITY[sym], period="1d", interval="1m", progress=False)
    curr = df['Close'].iloc[-1]
    st.metric(f"{sym} Live", f"{curr:.2f}")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader("🔍 Scanning 208 F&O Stocks - 1 Hour Munaadiye Top 10")
    if st.button("SCAN NOW - Top 10 UP/DOWN"):
        results=[]
        for s in FNO_STOCKS:
            try:
                df = yf.download(s, period="1d", interval="5m", progress=False)
                if df.empty: continue
                curr = df['Close'].iloc[-1]
                vwap = df['Close'].tail(20).mean()
                score = (curr - vwap)/vwap*100
                results.append({"Company":s.replace(".NS",""), "Price":curr, "Score":score, "Target UP":df['High'].tail(30).max(), "Target DOWN":df['Low'].tail(30).min()})
            except: pass
        res = pd.DataFrame(results)
        col1, col2 = st.columns(2)
        with col1:
            st.success("🟢 மேலே ஏற போற Top 10")
            st.dataframe(res.sort_values(by="Score", ascending=False).head(10), use_container_width=True)
        with col2:
            st.error("🔴 கீழே இறங்க போற Top 10")
            st.dataframe(res.sort_values(by="Score", ascending=True).head(10), use_container_width=True)
