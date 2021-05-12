import os
# путь к каталогу bet_bot
BET_PROJECT_ROOT = os.getenv('PYTHONPATH')

# путь к каталогу, где хранятся chrome данные
CHROME_DIR_PACKAGES = BET_PROJECT_ROOT + 'chrome_dir/'

# путь к данным сервера(каталог)
SERVER_DATA_PATH = BET_PROJECT_ROOT + 'server_data/'

# путь к файлу с инфой о всех последних постах
ALL_POSTS_JSON_PATH = SERVER_DATA_PATH + 'group_posts_data.json'

# путь до chrome_driver
CHROME_DRIVER_PATH = "/snap/bin/chromium.chromedriver"

# путь до базы данных
DATABASE_PATH = BET_PROJECT_ROOT + 'web_part/db.sqlite3'

# время ожидания по обновлению ссылок на матчи у бк с TAKES_MATCHES_LIVE=False
MATCHES_UPDATE_TIMEh = 12

MOZILLA_USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'

# ОПЛАТА
BASE_GROUP_PAYMENT = 7
BET_COMISSION = 0.02
