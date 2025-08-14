import streamlit as st
import pandas as pd
import yfinance as yf

# ---- 取得股價資料 ----
def get_stock_data(tickers, period="6mo"):
    data = yf.download(tickers, period=period, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        df = data["Adj Close"]
    else:
        df = data["Adj Close"].to_frame(name=tickers[0] if isinstance(tickers, list) else tickers)
    return df

# ---- 計算動能 ----
def compute_momentum(prices, w20, w60, w120):
    r20 = prices.pct_change(20) * 100
    r60 = prices.pct_change(60) * 100
    r120 = prices.pct_change(120) * 100
    score = r20 * w20 + r60 * w60 + r120 * w120
    df = pd.DataFrame({
        "20d %": r20.iloc[-1].round(2),
        "60d %": r60.iloc[-1].round(2),
        "120d %": r120.iloc[-1].round(2),
        "Score": score.iloc[-1].round(2),
    })
    return df.sort_values("Score", ascending=False)

# ---- 動能上色 ----
def color_func(val, max_s, min_s):
    if val >= max_s * 0.8:
        return "background-color: lightgreen"
    if val <= min_s * 1.2:
        return "background-color: lightcoral"
    return "background-color: khaki"

# ---- Streamlit UI ----
st.set_page_config(page_title="動能選股神器", layout="wide")
st.title("📈 動能選股神器")

st.sidebar.header("設定參數")
tickers_input = st.sidebar.text_input("股票代號（逗號分隔）", value="AAPL, MSFT, NVDA")
w20 = st.sidebar.slider("20天權重", 0.0, 1.0, 0.4, step=0.05)
w60 = st.sidebar.slider("60天權重", 0.0, 1.0, 0.35, step=0.05)
w120 = st.sidebar.slider("120天權重", 0.0, 1.0, 0.25, step=0.05)
tp_pct = st.sidebar.number_input("止賺 (%)", min_value=0.0, value=15.0, step=0.5)
sl_pct = st.sidebar.number_input("止蝕 (%)", min_value=0.0, value=8.0, step=0.5)

if st.sidebar.button("開始掃描"):
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    prices = get_stock_data(tickers)
    if prices.empty:
        st.error("無法取得股價，請確認代號正確")
    else:
        df = compute_momentum(prices, w20, w60, w120)
        last_price = prices.iloc[-1]
        df["Price"] = last_price.round(2)
        df["止賺價"] = (last_price * (1 + tp_pct/100)).round(2)
        df["止蝕價"] = (last_price * (1 - sl_pct/100)).round(2)

        max_s, min_s = df["Score"].max(), df["Score"].min()
        styled = df.style.applymap(lambda v: color_func(v, max_s, min_s), subset=["Score"])
        st.dataframe(styled, use_container_width=True)
