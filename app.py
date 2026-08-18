import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os, glob

st.set_page_config(page_title="Paitan Corp Live", layout="wide", page_icon="📈")
st.markdown("<style>.stMetric {background-color: #0E1117; border: 1px solid #30363d; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)
st.title("📈 Paitan Corp - All in One Live Dashboard [Auto Filter 4000 + 1H Predictor]")
st.success("✅ Auto Filter 4000 ON | Company Name Bug Fixed | 🔴 LIVE 1 HOUR PREDICTOR ON")

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def find_files():
    all_csv = glob.glob("*.csv")
    fno_file = None; all_file = None
    for f in all_csv:
        up = f.upper()
        if "F&O" in up or "MW-SECURITIES" in up or "FNO" in up: fno_file = f
        if "STOCKS" in up or "TRADED" in up or "ALL" in up:
            if all_file is None or os.path.getsize(f) > (os.path.getsize(all_file) if os.path.exists(all_file) else 0):
                if f!= fno_file: all_file = f
    if not all_file:
        for f in all_csv:
            if f!= fno_file: all_file = f
    return fno_file, all_file

fno_file, all_file = find_files()

# 1. NIFTY
st.header("1️⃣ NIFTY 50 - Live")
df_nifty = get_data("^NSEI")
if df_nifty is not None:
    c1,c2,c3 = st.columns(3)
    curr=float(df_nifty['Close'].iloc[-1])
    c1.metric("NIFTY Live", f"{curr:.2f}", f"{curr - float(df_nifty['Close'].iloc[-2]):.2f}")
    c2.metric("Buying Zone", f"{float(df_nifty['Low'].tail(30).min()):.2f}")
    c3.metric("Selling Zone", f"{float(df_nifty['High'].tail(30).max()):.2f}")
    fig=go.Figure(data=[go.Candlestick(x=df_nifty.index, open=df_nifty['Open'], high=df_nifty['High'], low=df_nifty['Low'], close=df_nifty['Close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
    st.plotly_chart(fig, width='stretch')
st.divider()

# 2. COMMODITY
st.header("2️⃣ COMMODITY - Live")
c1,c2,c3=st.columns(3)
for col,(name,sym) in zip([c1,c2,c3], [("GOLD","GC=F"),("SILVER","SI=F"),("CRUDE OIL","CL=F")]):
    df=get_data(sym)
    if df is not None:
        col.metric(name, f"{float(df['Close'].iloc[-1]):.2f}")
st.divider()

# 3. F&O DAILY FILE
st.header("3️⃣ F&O 208/224 Stocks - Daily File Top 10")
if fno_file:
    try:
        df_fno = pd.read_csv(fno_file)
        df_fno.columns = [c.strip().upper() for c in df_fno.columns]
        sym_c = next((c for c in df_fno.columns if 'SYMBOL' in c), 'SYMBOL')
        chg_c = next((c for c in df_fno.columns if 'CHANGE' in c), None)
        if chg_c:
            df_fno[chg_c] = pd.to_numeric(df_fno[chg_c].astype(str).str.replace(',',''), errors='coerce')
            df_fno = df_fno.dropna(subset=[chg_c]).sort_values(by=chg_c, ascending=False)
            c1,c2=st.columns(2)
            with c1: st.success(f"🟢 மேலே Top 10"); st.dataframe(df_fno.head(10), width='stretch')
            with c2: st.error(f"🔴 கீழே Top 10"); st.dataframe(df_fno.tail(10).sort_values(by=chg_c), width='stretch')
    except Exception as e: st.error(f"Error: {e}")

st.divider()

# 3.5 NEW - LIVE 1 HOUR PREDICTOR
st.header("3.5️⃣ 🔴 LIVE 1 HOUR PREDICTOR - 1 மணி நேரத்துக்கு முன்னாடி Signal")
st.warning("இது Live 5 நிமிஷ Candle-அ பார்த்து, அடுத்த 1 மணி நேரத்துல ஏற போற Stock-அ முன்கூட்டியே சொல்லும். F&O 208-ல இருந்து Top 20-அ Live Scan பண்ணும்.")

if st.button("🚀 START LIVE 1H PREDICTION SCAN"):
    # F&O File-ல இருந்து Symbol எடுக்கும்
    symbols_to_scan = []
    if fno_file:
        try:
            df_tmp = pd.read_csv(fno_file)
            col = next((c for c in df_tmp.columns if 'SYMBOL' in c.upper()), df_tmp.columns[0])
            symbols_to_scan = df_tmp[col].dropna().astype(str).tolist()[:20] # முதல் 20 மட்டும் Live - Speed-க்கு
        except: pass
    if not symbols_to_scan:
        symbols_to_scan = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","BHARTIARTL","ITC","LT","BAJFINANCE","TATASTEEL","WIPRO","ONGC","MARUTI","SUNPHARMA","TITAN","POWERGRID","NTPC","KOTAKBANK","ASIANPAINT"]

    results = []
    prog = st.progress(0)
    for i, s in enumerate(symbols_to_scan):
        yf_sym = f"{s}.NS" if not s.endswith(".NS") else s
        df = get_data(yf_sym)
        if df is None or len(df) < 20: continue

        try:
            curr = float(df['Close'].iloc[-1])
            vwap = float(df['Close'].tail(20).mean())
            avg_vol = float(df['Volume'].tail(20).mean())
            last_vol = float(df['Volume'].iloc[-1])
            vol_spike = last_vol / avg_vol if avg_vol > 0 else 1

            # 1H Prediction Logic
            score = (curr - vwap) / vwap * 100
            # Volume Spike + VWAP மேல இருந்தா 1 மணி நேரத்துல ஏறும்
            if score > 0.5 and vol_spike > 1.5:
                signal = "🟢 BUY - 1 மணி நேரத்துல ஏறும்"
                target = curr * 1.015
                reason = f"VWAP-க்கு மேல + Volume {vol_spike:.1f}x Spike"
            elif score < -0.5 and vol_spike > 1.5:
                signal = "🔴 SELL - 1 மணி நேரத்துல இறங்கும்"
                target = curr * 0.985
                reason = f"VWAP-க்கு கீழ + Volume {vol_spike:.1f}x Spike"
            else:
                signal = "🟡 WAIT"
                target = curr
                reason = "No Clear Breakout"

            results.append({
                "Company": s,
                "LTP": round(curr,2),
                "1H Signal": signal,
                "Target (1H)": round(target,2),
                "Reason": reason,
                "Score": round(score,2),
                "Vol Spike": f"{vol_spike:.1f}x"
            })
        except: pass
        prog.progress((i+1)/len(symbols_to_scan))

    if results:
        res_df = pd.DataFrame(results)
        # 1 மணி நேரத்துல ஏற போறத மட்டும் முதல்ல காமிக்கும்
        res_df_sorted = res_df.sort_values(by="Score", ascending=False)

        c_up, c_down = st.columns(2)
        with c_up:
            st.success("🟢 1 மணி நேரத்துல மேலே ஏற போறது - BUY LIST")
            st.dataframe(res_df_sorted[res_df_sorted['1H Signal'].str.contains('BUY')].head(10), width='stretch')
        with c_down:
            st.error("🔴 1 மணி நேரத்துல கீழே இறங்க போறது - SELL LIST")
            st.dataframe(res_df_sorted[res_df_sorted['1H Signal'].str.contains('SELL')].head(10), width='stretch')

        st.info("📊 முழு Live Scan Result:")
        st.dataframe(res_df_sorted, width='stretch')

st.divider()

# 4. ALL NSE 4000
st.header("4️⃣ ALL NSE 2500/4000 Stocks - EQ மட்டும் - Daily Top 10")
if all_file:
    try:
        df_all = pd.read_csv(all_file, low_memory=False)
        df_all.columns = [c.strip() for c in df_all.columns]
        sym_c = next((c for c in df_all.columns if 'SYMBOL' in c.upper()), df_all.columns[0])
        chg_c = next((c for c in df_all.columns if '%CHNG' in c.upper() or '% CHANGE' in c.upper()), None)
        series_c = next((c for c in df_all.columns if 'SERIES' in c.upper()), None)

        if series_c: df_eq = df_all[df_all[series_c].astype(str).str.upper() == 'EQ'].copy()
        else: df_eq = df_all.copy()

        if chg_c:
            df_eq[chg_c] = pd.to_numeric(df_eq[chg_c].astype(str).str.replace(',',''), errors='coerce')
            df_eq = df_eq.dropna(subset=[chg_c]).sort_values(by=chg_c, ascending=False)
            c1,c2=st.columns(2)
            with c1: st.success(f"🟢 ALL Market மேலே Top 10"); st.dataframe(df_eq.head(10)[[sym_c, chg_c]].head(10), width='stretch')
            with c2: st.error(f"🔴 ALL Market கீழே Top 10"); st.dataframe(df_eq.tail(10).sort_values(by=chg_c)[[sym_c, chg_c]].head(10), width='stretch')
    except Exception as e: st.error(f"Error: {e}")
