
import streamlit as st
import pandas as pd
import yfinance as yf

# ===== Helper Functions =====
def get_stock_data(tickers, period="6mo"):
    data = yf.download(tickers, period=period)

    # Handle MultiIndex columns (multiple tickers) or single ticker
    if isinstance(data.columns, pd.MultiIndex):
        return data["Adj Close"]
    else:
        return data.to_frame(name="Adj Close")

def calculate_momentum(prices):
    returns_20d = prices.pct_change(20).iloc[-1] * 100
    returns_60d = prices.pct_change(60).iloc[-1] * 100
    returns_120d = prices.pct_change(120).iloc[-1] * 100

    momentum_score = returns_20d * 0.4 + returns_60d * 0.35 + returns_120d * 0.25

    df = pd.DataFrame({
        "20d %": returns_20d.round(2),
        "60d %": returns_60d.round(2),
        "120d %": returns_120d.round(2),
        "Score": momentum_score.round(2)
    })

    return df.sort_values("Score", ascending=False)

def color_momentum(val, max_score, min_score):
    if val >= max_score * 0.8:
        return "background-color: lightgreen"
    elif val <= min_score * 1.2:
        return "background-color: lightcoral"
    else:
        return "background-color: khaki"

# ===== Streamlit App =====
st.set_page_config(page_title="📈 美股動能選股神器", layout="wide")
st.title("📈 美股動能選股神器")

# User Inputs
st.sidebar.header("設定參數")
default_tickers = "AAPL,MSFT,GOOGL,AMZN,NVDA"
tickers_input = st.sidebar.text_input("輸入股票代號（用逗號分隔）", value=default_tickers)
take_profit_pct = st.sidebar.number_input("止賺百分比 (%)", value=15.0, min_value=0.0, step=0.5)
stop_loss_pct = st.sidebar.number_input("止蝕百分比 (%)", value=8.0, min_value=0.0, step=0.5)

if st.sidebar.button("開始掃描"):
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    prices = get_stock_data(tickers)

    if prices.empty:
        st.error("無法取得股票數據，請檢查代號是否正確。")
    else:
        df_momentum = calculate_momentum(prices)
        latest_prices = prices.iloc[-1]

        df_momentum["Price"] = latest_prices.round(2)
        df_momentum["止賺價"] = (latest_prices * (1 + take_profit_pct/100)).round(2)
        df_momentum["止蝕價"] = (latest_prices * (1 - stop_loss_pct/100)).round(2)

        # Color coding without matplotlib dependency
        max_score = df_momentum["Score"].max()
        min_score = df_momentum["Score"].min()
        styled = df_momentum.style.applymap(lambda v: color_momentum(v, max_score, min_score), subset=["Score"])

        st.dataframe(styled, use_container_width=True)
