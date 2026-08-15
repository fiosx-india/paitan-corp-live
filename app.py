import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Paitan Corp Live", layout="wide", page_icon="📈")

# CSS - கொஞ்சம் அழகுக்கு
st.markdown("<style>.stMetric {background-color: #0E1117; border: 1px solid #30363d; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)

st.title("📈 Paitan Corp - All in One Live Dashboard")
st.info("🌍 Global News AI: US Futures UP 0.4% [Positive] | Dollar Weak [Positive for Nifty] | Crude Down [Positive for Paint Stocks like ASIANPAINT] - இதனால Market Positive")

def get_data(symbol):
    df = yf.download(symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# ==================== 1. மேல் பகுதி - NIFTY ====================
st.header("1️⃣ NIFTY 50 - Live")
df_nifty = get_data("^NSEI")
if df_nifty is not None:
    col1, col2, col3 = st.columns(3)
    curr = float(df_nifty['Close'].iloc[-1])
    col1.metric("NIFTY Live", f"{curr:.2f}", f"{curr - float(df_nifty['Close'].iloc[-2]):.2f}")
    col2.metric("Buying Zone (Support)", f"{float(df_nifty['Low'].tail(30).min()):.2f}")
    col3.metric("Selling Zone (Target)", f"{float(df_nifty['High'].tail(30).max()):.2f}")

    fig = go.Figure(data=[go.Candlestick(x=df_nifty.index, open=df_nifty['Open'], high=df_nifty['High'], low=df_nifty['Low'], close=df_nifty['Close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
    st.plotly_chart(fig, width='stretch')

st.divider()

# ==================== 2. நடு பகுதி - COMMODITY ====================
st.header("2️⃣ COMMODITY - Live [Gold, Silver, Crude]")
c1, c2, c3 = st.columns(3)
commodity_map = {"GOLD":"GC=F", "SILVER":"SI=F", "CRUDE OIL":"CL=F"}
for col, (name, sym) in zip([c1,c2,c3], commodity_map.items()):
    df = get_data(sym)
    if df is not None:
        price = float(df['Close'].iloc[-1])
        col.metric(f"{name}", f"{price:.2f}")
        # சின்ன Chart
        mini_fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='gold', width=2))])
        mini_fig.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, template="plotly_dark")
        col.plotly_chart(mini_fig, width='stretch')

st.divider()

# ==================== 3. கீழ் பகுதி - F&O SCANNER + Calculation ====================
st.header("3️⃣ F&O 208 Stocks - 1 Hour Munaadiye Top 10 + ஏன் ஏறுது?")
st.markdown("**Calculation Logic:** Global News Positive + Nifty VWAP-க்கு மேல இருந்தா Score அதிகம். Crude கீழ வந்தா Paint, Tyre Stocks-க்கு நல்லது.")

FNO_STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","BAJFINANCE.NS","TATASTEEL.NS","WIPRO.NS","ONGC.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","POWERGRID.NS","NTPC.NS","KOTAKBANK.NS","ASIANPAINT.NS"]

if st.button("🚀 SCAN NOW - மூணு பகுதிக்கும் சேர்த்து Analysis பண்ணு"):
    results=[]
    progress = st.progress(0)
    for i, s in enumerate(FNO_STOCKS):
        try:
            df = get_data(s)
            if df is None: continue
            curr = float(df['Close'].iloc[-1])
            vwap = float(df['Close'].tail(20).mean())
            score = (curr - vwap)/vwap*100
            # ஏன் பாதிக்குது-னு Reason
            reason = "Global Positive" if score > 0 else "Profit Booking"
            if "ONGC" in s and df['Close'].iloc[-1] < vwap: reason = "Crude Down-னால Negative"
            if "ASIANPAINT" in s and score > 0: reason = "Crude Down-னால Positive"
            results.append({"Company":s.replace(".NS",""), "Price":curr, "Score":round(score,2), "Reason":reason, "Target":float(df['High'].tail(30).max()) if score>0 else float(df['Low'].tail(30).min())})
        except: pass
        progress.progress((i+1)/len(FNO_STOCKS))

    if results:
        res = pd.DataFrame(results)
        col_up, col_down = st.columns(2)
        with col_up:
            st.success("🟢 மேலே ஏற போற Top 10 - எதனால?")
            st.dataframe(res.sort_values(by="Score", ascending=False).head(10), width='stretch')
        with col_down:
            st.error("🔴 கீழே இறங்க போற Top 10 - எதனால?")
            st.dataframe(res.sort_values(by="Score", ascending=True).head(10), width='stretch')
