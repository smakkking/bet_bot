# тута мы логиним всех пользователей, у кот время последнего логина либо null, либо меньше LOGIN_UPDATE_TIMEh
from datetime import datetime, timedelta
import time
import dateutil.parser

from multiprocessing import Pool

from global_constants import LOGIN_UPDATE_TIMEh, BOOKMAKER_OFFSET
from bet_manage import SQL_DB


def checking(x) :
    if (x['bookmaker_last_login'] is None) or \
            datetime.now() - dateutil.parser.parse(x['bookmaker_last_login']) > timedelta(hours=LOGIN_UPDATE_TIMEh):
        BOOKMAKER_OFFSET[x['bookmaker']].login(
            chdp=x['chrome_dir_path'],
            bkm_login=x['bookmaker_login'],
            bkm_password=x['bookmaker_password']
        )
        return str(x['id'])

def main(main_logger=None) :

    if main_logger :
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

    with Pool(processes=len(t)) as pool:
        update_db = list(pool.map(checking, t))

    update_str = ''
    for x in update_db :
        if x :
            update_str += ' or id=' + x
    update_str = update_str.replace('or', '', 1)

    q.SQL_UPDATE(set_cond="bookmaker_last_login=datetime('now')", where_cond=update_str)

    if main_logger :
        main_logger.info('{0:.2f} spent on relogin users'.format(time.time() - now))

if __name__ == "__main__" :
    main()
