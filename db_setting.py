import sqlite3

conn = sqlite3.connect("datafile.db")
cursor = conn.cursor()


cursor.execute(
    """create table if not exists cash (transaction_id integer primary key, user_id text not null, jp_yen integer, us_dollars real, comment varchar(30), date_info date)"""
)

cursor.execute(
    """create table if not exists stock (transaction_id integer primary key, user_id text not null, stock_id varchar(10), found_name text, stock_num integer, stock_price real, fee integer, tax integer, date_info date)"""
)

cursor.execute(
    """create table if not exists jp_tickers (ticker_id integer primary key, ticker_code text, found_name text, market text)"""
)

cursor.execute(
    """create table if not exists fgn_tickers (ticker_id integer primary key, ticker_code text, found_name text, market text)"""
)

conn.commit()
conn.close()
