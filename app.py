import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go, os, glob

st.set_page_config(page_title="Paitan Corp Live", layout="wide", page_icon="📈")
st.markdown("<style>.stMetric {background-color: #0E1117; border: 1px solid #30363d; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)
st.title("📈 Paitan Corp - All in One Live Dashboard [Auto Filter 4000]")
st.info("🌍 Auto Filter ON: Daily File பேர் என்னவா இருந்தாலும் தானா படிக்கும். 4000 Company வரை Support பண்ணும்.")

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def find_files():
    # Automatic-ஆ File-அ தேடும்
    all_csv = glob.glob("*.csv")
    fno_file = None
    all_file = None
    for f in all_csv:
        up = f.upper()
        if "F&O" in up or "MW-SECURITIES" in up or "FNO" in up:
            fno_file = f
        if "STOCKS" in up or "TRADED" in up or "ALL" in up or "2500" in up or "4000" in up:
            # StocksTraded.csv is bigger, so prefer it for all
            if all_file is None or os.path.getsize(f) > os.path.getsize(all_file):
                all_file = f
    return fno_file, all_file, all_csv

fno_file, all_file, all_csv = find_files()
st.caption(f"Found Files: F&O={fno_file} | ALL={all_file} | Total CSVs: {all_csv}")

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
        mini=go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='gold', width=2))])
        mini.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, template="plotly_dark")
        col.plotly_chart(mini, width='stretch')
st.divider()

# 3. F&O AUTO FILTER FROM CSV
st.header("3️⃣ F&O 208/224 Stocks - Auto File-ல இருந்து Top 10 [Daily File]")
if fno_file and os.path.exists(fno_file):
    try:
        df_fno = pd.read_csv(fno_file)
        # Clean % CHANGE column - it may have string
        df_fno['% CHANGE'] = pd.to_numeric(df_fno['% CHANGE'].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')
        df_fno = df_fno.dropna(subset=['% CHANGE'])
        df_fno = df_fno.sort_values(by='% CHANGE', ascending=False)
        
        col_up, col_down = st.columns(2)
        with col_up:
            st.success(f"🟢 இந்த பக்கம் Top 10 - மேலே ஏறுனது [{fno_file}]")
            st.dataframe(df_fno.head(10)[['SYMBOL','LTP','% CHANGE','VOLUME (shares)']], width='stretch')
        with col_down:
            st.error(f"🔴 அந்த பக்கம் Top 10 - கீழே இறங்குனது [{fno_file}]")
            st.dataframe(df_fno.tail(10).sort_values(by='% CHANGE')[['SYMBOL','LTP','% CHANGE','VOLUME (shares)']], width='stretch')
    except Exception as e:
        st.error(f"F&O File Read Error: {e}")
else:
    st.warning("F&O File கிடைக்கல. MW-SECURITIES File-அ Upload பண்ணுங்க.")

st.divider()

# 4. ALL 2500-4000 AUTO FILTER - EXTRA FEATURE
st.header("4️⃣ ALL NSE 2500/4000 Stocks - Auto Filter [Extra Feature] - EQ மட்டும்")
st.markdown("இது உன் பெரிய File-ல இருந்து Top Movers-அ Daily Automatic-ஆ எடுக்கும். Company மாறினாலும் பிரச்சனை இல்ல.")
if all_file and os.path.exists(all_file):
    try:
        # Large file may be big, read only needed
        df_all = pd.read_csv(all_file, low_memory=False)
        # Find % chng column - different names
        chg_col = None
        for c in df_all.columns:
            if '%CHNG' in c.upper() or '%CH' in c.upper(): chg_col = c; break
        
        # Filter EQ only if Series column exists
        if 'Series' in df_all.columns or 'SERIES' in df_all.columns:
            series_col = 'Series' if 'Series' in df_all.columns else 'SERIES'
            df_eq = df_all[df_all[series_col].str.upper() == 'EQ']
            st.caption(f"Total: {len(df_all)} | EQ Only: {len(df_eq)} (4000-ல இருந்து EQ மட்டும் Filter பண்ணியாச்சு)")
            df_show = df_eq
        else:
            df_show = df_all

        if chg_col:
            df_show[chg_col] = pd.to_numeric(df_show[chg_col].astype(str).str.replace(',',''), errors='coerce')
            df_show = df_show.dropna(subset=[chg_col]).sort_values(by=chg_col, ascending=False)
            
            c_up, c_down = st.columns(2)
            with c_up:
                st.success(f"🟢 ALL Market - மேலே Top 10 [{all_file}]")
                # Show Symbol, LTP, %chng
                cols_to_show = [col for col in ['Symbol','SYMBOL','LTP','%chng','% CHNG','Volume (Lakhs)'] if col in df_show.columns][:4]
                st.dataframe(df_show.head(10)[cols_to_show], width='stretch')
            with c_down:
                st.error(f"🔴 ALL Market - கீழே Top 10 [{all_file}]")
                st.dataframe(df_show.tail(10).sort_values(by=chg_col)[cols_to_show], width='stretch')
    except Exception as e:
        st.error(f"ALL File Read Error: {e} - File பெருசா இருக்கு, கொஞ்சம் Time ஆகும்")
else:
    st.warning("ALL NSE File கிடைக்கல. StocksTraded.csv Upload பண்ணுங்க.")
