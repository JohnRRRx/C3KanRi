import pandas as pd
import sqlite3

# CSV読み込み、3行目までskip，特定項目を残す
df = pd.read_csv(
    "./tikers/fgn.csv",
    encoding="shift-jis",
    skiprows=3,
    usecols=["ティッカー", "名称", "市場"],
)

# 項目名を変更
df.columns = ["ticker", "foundname", "market"]

# tickerの値を判断する関数作成
def ticker_check(row):
    ticker = row["ticker"]
    if str(ticker).isdigit():
        ticker = str(int(ticker))  # 数字化して先頭の0を除去
        if row["market"] == "香港市場":
            ticker += ".HK"
        elif row["market"] == "KOSPI":
            ticker += ".KS"
    return str(ticker)


# 各行のticker欄に、↑の関数で処理
df["ticker"] = df.apply(ticker_check, axis=1)
data_to_insert = list(zip(df["ticker"], df["foundname"], df["market"]))

conn = sqlite3.connect("datafile.db")
cursor = conn.cursor()

# 既存データ削除
cursor.execute("DELETE FROM fgn_tickers")

# 新規データ追加 (executemanyで一括追加)
cursor.executemany(
    """INSERT INTO fgn_tickers (ticker_code, found_name, market) VALUES (?, ?, ?)""",
    data_to_insert,
)

# 変更確定
conn.commit()
conn.close()
