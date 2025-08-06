# 投資記録  
[Link](https://c3kanri.onrender.com)  

 ## サービス概要  
投資した際に、通貨か株を選んで記録し、一覧表で全体像が確認できるアプリです。
  
 ## 開発背景  
WebAPIとPythonの学習の一環として開発しました。  
複数の証券口座や通貨を投資していく際に、投資全体像を手軽に把握できるを作ってみました。  
普段扱っている資産の種類(円、ドル、ETF)のみを対象にしております。

 ## 機能紹介
| ![](https://imgpoi.com/i/AYHODE.gif) | ![](https://imgpoi.com/i/AYH33V.gif)  | 
|:-----------:|:------------:|
|通貨(円/ドル)を記録する機能|株を記録する機能(銘柄コードと銘柄名のAutoComplete)|
| ![](https://imgpoi.com/i/AYHHTD.gif) | ![](https://imgpoi.com/i/AYHUZ2.gif) | 
|一覧表示機能(通貨、株、割合グラフ)|記録を削除する機能|
  
 ## 使用技術	

|           | 技術                |
|:---------:|:-------------------:|
| Frontend  | JavaScript, HTML, CSS, Bootstrap|
| Backend   | Python, Flask        |
| Database  | SQLite3              |
| Hosting   | Render               |
| Version Control | GitHub           |
| Web API   | GMOコインAPI（外国為替FX取得用）、<br>yfinance（株価データ取得用ライブラリ）|
