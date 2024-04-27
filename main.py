#!/usr/bin/env python
# coding: utf-8
from calendar import week
from importlib.resources import path
import os
from turtle import down
import slackweb
import urllib
import shutil
import sqlite3
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import subprocess
from sample import setting

# 設定ファイルの読み込み   
DATA_DIR_PATH = setting.DATA_DIR_PATH
WEB_DRIVER = setting.WEB_DRIVER
SLACK_CH_URL = setting.SLACK_CH_URL
PRE_URL_SAVE_FILE = setting.PRE_URL_SAVE_FILE
CRON_SET_FILE = setting.CRON_SET_FILE
EXECUTE_CMD = setting.EXECUTE_CMD

# 汎用定数の定義
DT_NOW = datetime.datetime.now()

def file_download(argURL):
    try:
        f = open(PRE_URL_SAVE_FILE,'r')
        # 先頭行よみこみ，改行をはぎとった文字列を取得
        pre_url = f.readline().strip()
        f.close()
        # 前回ダウンロードしたURLが記録されているファイルを開く(r+モード:ファイルを読み書き専用でオープンする)
        with open(PRE_URL_SAVE_FILE,'w') as f:
            # ダウンロードするURLを書き込み
            f.write(argURL + '\n')
            # 前回のURLと比較
            if(argURL != pre_url):
                #zipファイルをダウンロードする
                zip_file_path = DATA_DIR_PATH + DT_NOW.strftime('%Y-%m-%d') + '.zip'
                with urllib.request.urlopen(argURL) as download_file:
                    data = download_file.read()
                    with open(zip_file_path, mode='wb') as save_file:
                        save_file.write(data)

                # ダウンロードデータの一時保存場所を作成
                os.mkdir(DATA_DIR_PATH + 'TmpSave')
                # ダウンロードしたzipを解凍し，解凍されたディレクトリをTmpSaveディレクトリに保存
                shutil.unpack_archive(zip_file_path, DATA_DIR_PATH + 'TmpSave') 

                # 解凍したディレクトリ名を取得
                downloaded_dir = str(os.listdir(DATA_DIR_PATH + 'TmpSave')[0])
                # 解凍したディレクトリの中身を取得
                files = os.listdir(DATA_DIR_PATH + 'TmpSave/' + downloaded_dir)
                cross_file = DATA_DIR_PATH + 'TmpSave/' + downloaded_dir + '/' + files[0]
                len_df = add_db(cross_file)
                shutil.rmtree(DATA_DIR_PATH + 'TmpSave')
                return 'JARTIC交通事故データ取得成功!\n' + '取得データ件数:' + len_df + '件'
            else:#同じURLをダウンロードしようとしたらのパス
                with open(CRON_SET_FILE,'a') as f:
                    # 曜日を数字に変換
                    weekday = (datetime.date.today().weekday() + 1) 
                    # ’分 時 日付 月 曜日’の文字列
                    execute_time = (DT_NOW + datetime.timedelta(days = 7)).strftime('%-M %-H %-d %-m ') + str(weekday)
                    # ファイルの中身を設定
                    execute_txt = execute_time + ' ' + EXECUTE_CMD + '\n'
                    print('/n')
                    print(execute_txt)
                    f.write(execute_txt)
                # crontabにcronjob.txtの内容を登録
                subprocess.run([f"crontab {CRON_SET_FILE}"], shell=True)
                # 7日後に実行する処理を，テキストファイルから消しておく
                with open(CRON_SET_FILE,'r') as f:
                    data_lines = f.read()
                # 最後にある登録コマンドを，改行コードに置換して削除しておく
                data_lines = data_lines.replace(execute_txt,'')
                with open(CRON_SET_FILE,'w') as f:
                    f.write(data_lines)
                raise Exception
    except:
        return 'JARTIC交通事故データ取得失敗!'

def slack_notification(argStatus):
    # SlackのチャンネルAPI
    slack = slackweb.Slack(url = SLACK_CH_URL)
    slack.notify(text = argStatus)

def add_db(argFile):
    #sqlite3がshift_jisに対応していないのでutf-8に変更
    now = DT_NOW.strftime('%Y-%m-%d') + '.csv'
    with open(argFile, encoding='shift_jis') as f_in:
        with open(DATA_DIR_PATH + now, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
    # csvをデータフレームオブジェクトに変換
    df = pd.read_csv(DATA_DIR_PATH + now,encoding='utf-8')  
    #dbに接続(dbがなかったら新規作成される)
    conn = sqlite3.connect(DATA_DIR_PATH + "traffic.db")
    df.to_sql('traffic_volume',conn,if_exists='append',index=None)
    # カーソルを取得
    cur = conn.cursor()
    # バックアップを最新にするために，古いバックアップを消す
    cur.execute('DROP TABLE IF EXISTS traffic_volume_bk')
    # traffic_volumeテーブルのバックアップ作成
    cur.execute('CREATE TABLE traffic_volume_bk AS SELECT * FROM traffic_volume')    
    # dbの接続を切断
    conn.close()
    return str(len(df))

def scraping():
    # ウェブドライバーのオプション設定，ヘッドレスモードを有効にする
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(WEB_DRIVER,options = options)
    # JARTICのURLに遷移
    driver.get('https://www.jartic.or.jp/')
    # 明示的な待機,find_element_by_idの要素が見つかるまで最大10秒待機する
    driver.implicitly_wait(10)
    # iframe要素を取得
    iframe = driver.find_element_by_id('contents')
    # 操作対象ウィンドウをiframeに変更(変更しないと，要素が検索できない)
    driver.switch_to.frame(iframe)
    # モーダルの同意ボタンの要素を取得して，クリック
    modal_btn = driver.find_element_by_css_selector('#termsModal > div > div > div.terms-btn-area > div:nth-child(1)')
    modal_btn.click()
    # 各種情報の提供(オープンデータ)のページに遷移
    link_hover = driver.find_element_by_css_selector('#global-nav > ul > li:nth-child(1) > p')
    #ActionChainsのインスタンスを作成
    driver_action = ActionChains(driver)
    #perfom処理でホバー
    driver_action.move_to_element(link_hover).perform()
    link_btn = driver.find_element_by_css_selector('#global-nav > ul > li:nth-child(1) > div > ul > li.is-pc > a')
    link_btn.click()
    # 愛知県データのリンクを検索して，取得
    data_link = driver.find_element_by_css_selector('#openDataList > div > div:nth-child(2) > ul > li:nth-child(27) > a')
    download_href = data_link.get_attribute('href')
    driver.quit()
    return str(download_href)

if __name__ == "__main__":
    # crontabにcronjob.txtの内容を設定
    subprocess.run([f"crontab {CRON_SET_FILE}"], shell=True)
    # スクレイピングしてダウンロードするURLを返り値として受け取る
    download_url = scraping()
    # 指定した引数であるURLのファイルのダウンロードして，取得可否(結果)を返り値として受け取る
    request_status = file_download(download_url)
    # スラックにメッセージを送信する．
    slack_notification(request_status)