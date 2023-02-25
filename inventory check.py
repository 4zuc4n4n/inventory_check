# coding: UTF-8
import re
import requests
import json
import time
import pyshorteners
from selenium import webdriver
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
from pyshorteners import Shortener

LINE_ACCESS_TOKEN = "LINEアクセストークン"
LINE_USER_ID = "LINE通知先ID"
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
#Chromeドライバの設定
CHROMEDRIVER = '/usr/local/bin/chromedriver'
URL = "https://www.amazon.co.jp/"
user_profile = '/root/.config/google-chrome/Default'

chrome_service = fs.Service(executable_path=CHROMEDRIVER)
options = Options()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument(f'service={chrome_service}')
options.add_argument("--disable-dev-shm-usage")
options.add_argument('user-data-dir=' + user_profile)
driver = webdriver.Chrome(options=options)

# UA偽装用
my_header = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; NP06; rv:11.0) like Gecko"
}

#URL名短縮
sh = pyshorteners.Shortener()

# 確認したい商品のURL,配列にURLを追加すれば複数の商品の在庫が確認できる
amazon_url = [
    "https://www.amazon.co.jp/###############"
]

# discord通知時の文字列
result_str = "通知用"

#amazonホーム画面
aurl = "https://www.amazon.co.jp/"

#画面遷移
driver.get('https://www.amazon.co.jp/')
element = driver.find_element_by_id("glow-ingress-line1")
#print(element.text)
if("こんにちは" in element.text) == True: # ログインしてなかったらログインする
    print ("ログインする")

    # ログイン画面へ遷移
    mailad = driver.find_element_by_id("nav-link-accountList")
    mailad.click()

    # ログインIDを入力
    login_id = driver.find_element_by_id("ap_email")
    login_id.send_keys('ログインしたいアカウントのメールアドレス')

    # 「次に進む」をクリック
    nextb = driver.find_element_by_class_name("a-button-input")
    nextb.click()
    time.sleep(3)

    # パスワードを入力
    password = driver.find_element_by_name("password")
    password.send_keys('ログインしたいアカウントのパスワード')

    # 「ログイン」をクリック
    nextb = driver.find_element_by_id("signInSubmit")
    nextb.click()
    time.sleep(3)
    cur_url = driver.current_url
else: #ログイン後の処理
    pass

# Amazon用
result_str = "●●Amazon●●\n"
for i in range(len(amazon_url)):
    data = requests.get(amazon_url[i], headers = my_header)
    data.encoding = data.apparent_encoding
    data = data.text
    soup = BeautifulSoup(data, "html.parser")
    try:
        detail0 = soup.find('div', id="tabular_feature_div")
        detail = detail0.find('a').text
        #print(detail) # デバッグ
        if ("Amazon" in detail):
            #print(detail) # デバッグ
            url = sh.tinyurl.short(amazon_url[i])
            driver.get(amazon_url[i])
            mailad = driver.find_element_by_id('add-to-cart-button')
            mailad.click()
            cur_url = driver.current_url
            result_str += " 在庫あり\n" + cur_url + "\n\n"
    except AttributeError:
            print("Error2_1")

# LINEへ通知
if result_str != "●●Amazon●●\n":
    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=result_str))
    except AttributeError:
         print("Error2_2")