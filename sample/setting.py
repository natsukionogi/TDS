# データを保存するディレクトリのパス
DATA_DIR_PATH = '/Users/user/Desktop/labroom/TDS/TrafficData/'
# スクレイピングするwebdriverのパス
WEB_DRIVER = '/Users/user/Desktop/labroom/TDS/WebDriver/chromedriver'
# slackのincoming-webhookを利用するチャンネルのAPIURL
SLACK_CH_URL = 'setup ur api key'
# 前回ダウンロードしたURLが記載されているテキストファイルのパス
PRE_URL_SAVE_FILE = '/Users/user/Desktop/labroom/TDS/Sample/preurl.txt'
# crontab -eに登録するテキストファイルのパス
CRON_SET_FILE = '/Users/user/Desktop/labroom/TDS/Sample/cronjob.txt'
# cronで実行するコマンドと，その引数である実行ファイルの絶対パス
EXECUTE_CMD = '/Users/user/.pyenv/versions/3.9.7/bin/python /Users/user/Desktop/labroom/TDS/main.py'