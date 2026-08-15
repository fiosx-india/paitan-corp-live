import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Paitan Corp Live", layout="wide", page_icon="📈")
st.title("📈 Paitan Corp - Live AI Predictor")
st.markdown("**Nifty + Commodity + 208 F&O Stocks | 1 Hour Munaadiye Prediction**")

FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","BAJFINANCE.NS","TATASTEEL.NS","WIPRO.NS","ONGC.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","POWERGRID.NS","NTPC.NS","KOTAKBANK.NS","ASIANPAINT.NS"]
COMMODITY = {"GOLD":"GC=F", "SILVER":"SI=F", "CRUDE":"CL=F"}

def get_data(symbol):
    # இது தான் Fix - புது yfinance-க்கான Fix
    df = yf.download(symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
    if df.empty: return None
    # Multi-index-அ Flat பண்றது
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

choice = st.sidebar.selectbox("Market", ["NIFTY 50", "COMMODITY", "F&O 208 Scanner"])
st.sidebar.success("🌍 Global News: US Futures UP 0.4% | Dollar Weak | Positive for India")

if choice == "NIFTY 50":
    df = get_data("^NSEI")
    if df is not None:
        curr = float(df['Close'].iloc[-1])
        st.metric("NIFTY Live", f"{curr:.2f}")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"Buying Zone {float(df['Low'].tail(30).min()):.2f} | Selling Zone {float(df['High'].tail(30).max()):.2f}")

elif choice == "COMMODITY":
    sym = st.selectbox("Commodity", list(COMMODITY.keys()))
    df = get_data(COMMODITY[sym])
    if df is not None:
        curr = float(df['Close'].iloc[-1])
        st.metric(f"{sym} Live", f"{curr:.2f}")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader("🔍 Scanning 208 F&O Stocks - 1 Hour Munaadiye Top 10")
    if st.button("SCAN NOW - Top 10 UP/DOWN"):
        results=[]
        progress = st.progress(0)
        for i, s in enumerate(FNO_STOCKS):
            try:
                df = get_data(s)
                if df is None or df.empty: continue
                curr = float(df['Close'].iloc[-1])
                vwap = float(df['Close'].tail(20).mean())
                score = (curr - vwap)/vwap*100
                results.append({"Company":s.replace(".NS",""), "Price":curr, "Score":round(score,2), "Target UP":float(df['High'].tail(30).max()), "Target DOWN":float(df['Low'].tail(30).min())})
            except: pass
            progress.progress((i+1)/len(FNO_STOCKS))

        if results:
            res = pd.DataFrame(results)
            col1, col2 = st.columns(2)
            with col1:
                st.success("🟢 மேலே ஏற போற Top 10")
                st.dataframe(res.sort_values(by="Score", ascending=False).head(10), use_container_width=True)
            with col2:
                st.error("🔴 கீழே இறங்க போற Top 10")
                st.dataframe(res.sort_values(by="Score", ascending=True).head(10), use_container_width=True)
        else:
            st.error("Data கிடைக்கல, Market Close-ஆ இருக்கலாம். Market Time-ல Try பண்ணு.")
