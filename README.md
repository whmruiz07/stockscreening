# 動能選股 Momentum Dashboard

這是一個使用 Streamlit + yfinance 製作的美股動能選股工具，功能包含：
- 支援多股票 / 單股票輸入
- 自訂短中長期動能參數與權重
- 顏色顯示動能強弱、RSI、距 52 週高點距離
- 顯示建議止蝕 / 止賺價（ATR 倍數計算）
- 快速篩選條件（如近 20 日 ≥ 7%、距 52W 高 ≤ 5%、RSI 40–60）
- 避免 yfinance 的 Adj Close KeyError

## 安裝
```bash
pip install -r requirements.txt
```

## 執行
```bash
streamlit run streamlit_app.py
```

## 檔案結構
- `streamlit_app.py` — 主程式
- `requirements.txt` — 依賴套件
- `README.md` — 使用說明
