
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="India Market",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

INDEXES = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "INDIA VIX": "^INDIAVIX",
    "SENSEX": "^BSESN",
}

NIFTY50 = [
    "ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK",
    "BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BEL","BHARTIARTL",
    "CIPLA","COALINDIA","DRREDDY","EICHERMOT","ETERNAL",
    "GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO",
    "HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY",
    "ITC","JIOFIN","JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI",
    "MAXHEALTH","NESTLEIND","NTPC","ONGC","POWERGRID","RELIANCE",
    "SBILIFE","SBIN","SHRIRAMFIN","SUNPHARMA","TATACONSUM",
    "TATASTEEL","TCS","TECHM","TITAN","TRENT","ULTRACEMCO","WIPRO"
]

WATCHLIST = [
    "HDFCBANK","ICICIBANK","AXISBANK","KOTAKBANK",
    "BAJFINANCE","SBIN","INDUSINDBK",
    "GLASSWALL","KANOHAR","KARAMTARA"
]

@st.cache_data(ttl=30, show_spinner=False)
def get_quotes(symbols):
    rows = []
    for symbol in symbols:
        ysym = symbol if symbol.startswith("^") else f"{symbol}.NS"
        try:
            h = yf.Ticker(ysym).history(period="5d", interval="1d", auto_adjust=False)
            if h.empty:
                continue
            close = float(h["Close"].iloc[-1])
            prev = float(h["Close"].iloc[-2]) if len(h) > 1 else close
            chg = close - prev
            pct = chg / prev * 100 if prev else 0
            rows.append({"Symbol": symbol, "Price": close, "Change": chg, "Pct": pct})
        except Exception:
            pass
    return pd.DataFrame(rows)

def tile(row):
    pct = float(row.Pct)
    if pct > 0.05:
        bg = "rgba(0,160,80,.30)"
        txt = f"+{pct:.2f}%"
    elif pct < -0.05:
        bg = "rgba(220,40,55,.30)"
        txt = f"{pct:.2f}%"
    else:
        bg = "rgba(130,130,130,.16)"
        txt = f"{pct:.2f}%"
    return f"""
    <div style="background:{bg};border-radius:8px;padding:8px 4px;
                margin:2px;text-align:center;border:1px solid rgba(0,0,0,.08)">
      <b style="font-size:13px">{row.Symbol}</b><br>
      <span style="font-size:12px">₹{row.Price:,.2f}</span><br>
      <b style="font-size:12px">{txt}</b>
    </div>
    """

st.title("📈 India Market")
st.caption("Mobile NSE-style market monitor")

now = datetime.now(ZoneInfo("Asia/Kolkata"))
st.caption(now.strftime("%d-%b-%Y • %H:%M:%S IST"))

# Top index cards in a 2-column mobile-friendly layout
idx = get_quotes(list(INDEXES.values()))
reverse = {v:k for k,v in INDEXES.items()}
if not idx.empty:
    idx["Name"] = idx.Symbol.map(reverse)
    for start in range(0, len(idx), 2):
        c = st.columns(2)
        for col, (_, r) in zip(c, idx.iloc[start:start+2].iterrows()):
            col.metric(r.Name, f"₹{r.Price:,.2f}", f"{r.Pct:+.2f}%")

st.divider()

tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "⭐ Watchlist", "📊 Breadth"])

with tab1:
    st.subheader("NIFTY 50")
    heat = get_quotes(NIFTY50)
    if heat.empty:
        st.warning("Market data unavailable.")
    else:
        heat = heat.sort_values("Pct", ascending=False).reset_index(drop=True)
        for start in range(0, len(heat), 3):
            cols = st.columns(3)
            for col, (_, r) in zip(cols, heat.iloc[start:start+3].iterrows()):
                with col:
                    st.markdown(tile(r), unsafe_allow_html=True)

with tab2:
    st.subheader("My Watchlist")
    watch = get_quotes(WATCHLIST)
    if watch.empty:
        st.warning("No watchlist data.")
    else:
        for _, r in watch.iterrows():
            c1, c2, c3 = st.columns([1.3, 1, .8])
            c1.write(f"**{r.Symbol}**")
            c2.write(f"₹{r.Price:,.2f}")
            c3.write(f"{r.Pct:+.2f}%")

with tab3:
    st.subheader("Market Breadth")
    if not heat.empty:
        adv = int((heat.Pct > 0).sum())
        dec = int((heat.Pct < 0).sum())
        unch = int((heat.Pct.abs() <= .05).sum())
        st.metric("Advances", adv)
        st.metric("Declines", dec)
        st.metric("Unchanged", unch)

st.divider()
st.caption("Data source in this starter: yfinance. It is not an NSE licensed real-time feed. Do not use it as the sole source for trading or order execution.")
