import pandas as pd
import sqlite3

# xls読み込み、特定項目のみ取得
df = pd.read_excel("./tikers/jp.xls", usecols=["コード", "銘柄名", "市場・商品区分"])

# # 項目名を変更
df.columns = ["ticker", "foundname", "market"]

# tickerの値を判断する関数作成
def ticker_check(row):
    ticker = str(row["ticker"]) + ".T"
    return str(ticker)

# # 各行のticker欄に、↑の関数で処理
df["ticker"] = df.apply(ticker_check, axis=1)

data_to_insert = list(zip(df["ticker"], df["foundname"], df["market"]))

conn = sqlite3.connect("datafile.db")
cursor = conn.cursor()

# 既存データ削除
cursor.execute("DELETE FROM jp_tickers")

# 新規データ追加 (executemanyで一括追加)
cursor.executemany(
    """INSERT INTO jp_tickers (ticker_code, found_name, market) VALUES (?, ?, ?)""",
    data_to_insert,
)

# 変更確定
conn.commit()
conn.close()
