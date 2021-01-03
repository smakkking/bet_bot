# путь к каталогу bet_bot
BET_PROJECT_ROOT = '/home/andreysm/bet_bot/'

# путь к каталогу, где хранятся chrome данные
CHROME_DIR_PACKAGES = BET_PROJECT_ROOT + '/chrome_dir/'

# путь к данным сервера(каталог)
SERVER_DATA_PATH = BET_PROJECT_ROOT + '/server_data/'

# путь к файлу с инфой о всех последних постах
ALL_POSTS_JSON_PATH = SERVER_DATA_PATH + '/group_posts_data.json'

# путь до chrome_driver
CHROME_DRIVER_PATH = "/snap/bin/chromium.chromedriver"

# путь до базы данных
DATABASE_PATH = BET_PROJECT_ROOT + '/web_part/db.sqlite3'

# время ожидания по обновлению ссылок на матчи у бк с TAKES_MATCHES_LIVE=False
MATCHES_UPDATE_TIMEh = 12

# время ожидания по обновлению логинов
LOGIN_UPDATE_TIMEh = 24

from moduls.bookmaker_moduls import BETSCSGO_betting
from moduls.group_moduls import ExpertMnenie_group, CSgoVictory_group, BETSPEDIA_group

GROUP_OFFSET = {
    ExpertMnenie_group.NAME: ExpertMnenie_group,
    CSgoVictory_group.NAME: CSgoVictory_group,
    BETSPEDIA_group.NAME: BETSPEDIA_group,
}

BOOKMAKER_OFFSET = {
    BETSCSGO_betting.NAME: BETSCSGO_betting,
}
