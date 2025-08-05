import pandas as pd

# csv読み込み、3行目までskip，shift-jisでencode
df = pd.read_csv("./tikers/fgn.csv", encoding="shift-jis", skiprows=3)

# 欲しい項目だけ残す
columns_to_keep = ["ティッカー", "名称", "市場"]
df_filtered = df[columns_to_keep].copy()

# 項目名を変更
df_filtered.columns = ["ticker", "foundname", "market"]

# ticker処理
def process_ticker(row):
    ticker = row["ticker"]
    market = row["market"]

    # 全桁數字の場合
    if str(ticker).isdigit():
        # 一度数字化し、先頭の0を除去
        ticker = str(int(ticker))
        if market == "香港市場":
            ticker += ".HK"
        elif market == "KOSPI":
            ticker += ".KS"
    # それ以外はそのまま保存
    else:
        ticker = str(ticker)

    return ticker


# # 應用處理函數
# df_filtered["ticker"] = df_filtered.apply(process_ticker, axis=1)

# # 移除可能存在的 NaN 值
# df_filtered = df_filtered.dropna()

# # 印出結果
# headers = df_filtered.columns.tolist()
# print(headers)

# # 印出每一行數據
for _, row in df_filtered.iterrows():
    print([row["ticker"], row["foundname"], row["market"]])
