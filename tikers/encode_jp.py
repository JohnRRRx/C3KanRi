import pandas as pd
import sqlite3

# xls読み込み、特定項目のみ取得
df = pd.read_excel("./tikers/jp.xls", usecols=["コード", "銘柄名", "市場・商品区分"])

# # 項目名を変更
df.columns = ["ticker", "foundname", "market"]

# tickerにある全データを文字列に変換し、文字列を1個ずつ小数点があった場合は区切って
# 最初の4文字を.Tと結合 (ifで1個ずつ判定するより効率的+)
df["ticker"] = df["ticker"].astype(str).str.split(".").str[0] + ".T"

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
