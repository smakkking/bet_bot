# тута мы логиним всех пользователей, у кот время последнего логина либо null, либо меньше LOGIN_UPDATE_TIMEh
from datetime import datetime, timedelta
import time
import dateutil.parser

from global_constants import LOGIN_UPDATE_TIMEh, BOOKMAKER_OFFSET
from bet_manage import SQL_DB


def main(debug=False) :

    if debug :
        now = time.time()

    q = SQL_DB()
    t = q.SQL_SELECT(
        select_cond= [
            'id', 'bookmaker_last_login',
            'chrome_dir_path', 'bookmaker',
            'bookmaker_login', 'bookmaker_password'
        ],
        where_cond='sub_status=1',
    )
    update_db = []
    for x in t :
        if (x['bookmaker_last_login'] is None) or \
                datetime.now() - dateutil.parser.parse(x['bookmaker_last_login']) > timedelta(hours=LOGIN_UPDATE_TIMEh) :
            BOOKMAKER_OFFSET[x['bookmaker']].login(
                chdp=x['chrome_dir_path'],
                bkm_login=x['bookmaker_login'],
                bkm_password=x['bookmaker_password']
            )
            update_db.append(str(x['id']))

    update_str = ''
    for x in update_db :
        update_str += ' and id=' + x
    update_str = update_str.replace('and', '', 1)

    q.SQL_UPDATE(set_cond="bookmaker_last_login=datetime(" + str(int(time.time())) + ", 'unixepoch')", where_cond=update_str)

    if debug :
        print('{0:.2f} spent on relogin users'.format(time.time() - now))
