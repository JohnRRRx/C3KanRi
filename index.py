import math
import sqlite3
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
import japanize_matplotlib
import os
import uuid
from flask import Flask, g, redirect, render_template, request, session

matplotlib.use("agg")

endPoint = "https://forex-api.coin.z.com/public"
path = "/v1/ticker"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
database = "datafile.db"


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = sqlite3.connect(database)
    return g.sqlite_db


def close_db(exception):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.before_request
def assign_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())


@app.route("/")
def top():
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    result = cursor.execute("select * from cash where user_id = ?", (user_id,))
    cash_result = result.fetchall()

    # 円とドルの総額を計算
    jp_yen = 0
    us_dollars = 0
    for data in cash_result:
        jp_yen += data[2]
        us_dollars += data[3]

    # 為替レートを取得
    response = requests.get(endPoint + path)
    rate = response.json()["data"][0]
    symbol, jpy_to_usd, usd_to_jpy, timestamp, status = rate.values()
    total = math.floor(jp_yen + us_dollars * float(usd_to_jpy))
    data = {
        "total": total,
        "jpy_to_usd": float(jpy_to_usd),
        "usd_to_jpy": float(usd_to_jpy),
        "jp_yen": jp_yen,
        "us_dollars": us_dollars,
        "usd": us_dollars,
        "jpy": jp_yen,
        "cash_result": cash_result,
    }
    # 株データを取得
    result2 = cursor.execute("select * from stock where user_id = ?", (user_id,))
    stock_result = result2.fetchall()
    unqiue_stock_list = []
    for data2 in stock_result:
        if data2[2] not in unqiue_stock_list:
            unqiue_stock_list.append(data2[2])
    # # 時価総額を計算
    total_stock_value = 0

    # 銘柄別データを計算
    stock_info = []
    for stock in unqiue_stock_list:
        result = cursor.execute(
            "select * from stock where stock_id = ? and user_id = ?", (stock, user_id)
        )
        result = result.fetchall()
        stock_cost = 0  # 単一株総コスト
        shares = 0  # 単一株総所持数
        for d in result:
            shares += int(d[4])  # 約定株数を累計
            stock_cost += (
                d[4] * d[5] + d[6] + d[7]
            )  # 約定株数 x 約定単価 + 手数料 + 課税額

        # 現在株価を取得
        stock_code = yf.Ticker(stock)
        latest_info = stock_code.info
        current_price = latest_info["regularMarketPrice"]
        # history = stock_code.history(period="1d")
        # close_price = float(history["Close"].iloc[-1])
        # print(stock,history)
        # 1銘柄の時価総額
        total_value = round(shares * current_price, 2)
        total_stock_value += total_value
        # 1銘柄の平均取得単価
        average_cost = round(stock_cost / shares, 2)
        # 1銘柄のリターン率
        rate_of_return = round((total_value - stock_cost) * 100 / stock_cost, 2)
        stock_info.append(
            {
                "stock_id": stock,
                "found_name": d[3],
                "stock_cost": stock_cost,
                "total_value": total_value,
                "average_cost": average_cost,
                "shares": shares,
                "current_price": current_price,
                "rate_of_return": rate_of_return,
            }
        )

    for stock in stock_info:
        stock["value_percentage"] = round(
            stock["total_value"] * 100 / total_stock_value, 2
        )

    # 株の円グラフを作成
    if len(unqiue_stock_list) != 0:
        labels = tuple(unqiue_stock_list)
        size = [d["total_value"] for d in stock_info]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(size, labels=None, autopct="%1.1f%%", shadow=None)
        ax.legend(labels=labels, loc="upper right")
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.savefig("static/stock_piechart.jpg", dpi=200)
    else:
        try:
            os.remove("static/stock_piechart.jpg")
        except:
            pass

    # 資産全体の円グラフを作成
    if us_dollars != 0 or jp_yen != 0 or total_stock_value != 0:
        labels = tuple(["米ドル", "日本円", "株"])
        size = [us_dollars * float(usd_to_jpy), jp_yen, total_stock_value]

        # 割合が0の資産を表示しない
        filtered_labels = []
        filtered_size = []
        for i in range(len(size)):
            if size[i] > 0:
                filtered_labels.append(labels[i])
                filtered_size.append(size[i])
        if filtered_size:
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.pie(filtered_size, labels=None, autopct="%1.1f%%", shadow=None)
            ax.legend(labels=filtered_labels, loc="upper right")
            fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.savefig("static/assets_piechart.jpg", dpi=200)
    else:
        try:
            os.remove("static/assets_piechart.jpg")
        except:
            pass

    data["stock_info"] = stock_info
    data.update(
        {
            "show_stock_piechart": os.path.exists("static/stock_piechart.jpg"),
            "show_assets_piechart": os.path.exists("static/assets_piechart.jpg"),
        }
    )
    return render_template("top.html", data=data)


@app.route("/cash")
def cash_form():
    return render_template("cash.html")


@app.route("/cash", methods=["POST"])
def submit_cash():
    # 金額と日付を取得
    jp_yen = 0
    us_dollars = 0
    if request.values["jp_yen"] != "":
        jp_yen = request.values["jp_yen"]
    if request.values["us_dollars"] != "":
        us_dollars = request.values["us_dollars"]
    comment = request.values["comment"]
    date = request.values["date_info"]

    # dbに更新
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """insert into cash (user_id, jp_yen, us_dollars, comment, date_info) values (?, ?, ?, ?, ?)""",
        (user_id, jp_yen, us_dollars, comment, date),
    )
    conn.commit()
    return redirect("/")  # returnがないとエラーになる


@app.route("/cash_delete", methods=["POST"])
def cash_delete():
    user_id = session["user_id"]
    transaction_id = request.values["id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "delete from cash where transaction_id = ? and user_id = ?",
        (transaction_id, user_id),
    )
    conn.commit()
    return redirect("/")


@app.route("/stock")
def stock_form():
    return render_template("stock.html")


@app.route("/stock", methods=["POST"])
def submit_stock():
    # 株データ、日付などを取得
    stock_id = request.values["stock_id"]
    found_name = request.values["found_name"]
    stock_num = request.values["stock_num"]
    stock_price = request.values["stock_price"]
    fee = 0
    tax = 0
    if request.values["fee"] != "":
        fee = request.values["fee"]
    if request.values["tax"] != "":
        tax = request.values["tax"]
    date = request.values["date_info"]

    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """insert into stock (user_id, stock_id, found_name, stock_num, stock_price, fee, tax, date_info) values (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, stock_id, found_name, stock_num, stock_price, fee, tax, date),
    )
    # print(stock_id,found_name, stock_num, stock_price, fee, tax, date)
    conn.commit()
    return redirect("/")
    return render_template("/")


@app.route("/api/search_ticker", methods=["GET"])
def search_ticker():
    query = request.args.get("q", "").strip()

    if not query:
        return {"results": []}

    conn = get_db()
    cursor = conn.cursor()

    try:
        sql_query = """
        SELECT DISTINCT ticker_code, found_name FROM jp_tickers 
        WHERE ticker_code LIKE ? 
        UNION 
        SELECT DISTINCT ticker_code, found_name FROM fgn_tickers 
        WHERE ticker_code LIKE ?
        ORDER BY ticker_code
        LIMIT 5
        """

        search_term = f"%{query}%"
        cursor.execute(sql_query, (search_term, search_term))
        results = cursor.fetchall()

        ticker_list = []
        for row in results:
            ticker_list.append({"ticker_code": row[0], "found_name": row[1]})
        # print(ticker_list)
        return {"results": ticker_list}
    except:
        print("Error")


@app.route("/stock_delete", methods=["POST"])
def stock_delete():
    user_id = session["user_id"]
    stock_id = request.values["id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "delete from stock where stock_id = ? and user_id = ?", (stock_id, user_id)
    )
    conn.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
