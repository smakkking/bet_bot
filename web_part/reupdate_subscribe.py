from manage import DATABASE_PATH
import sqlite3
from sqlite3 import Error
from moduls.bet_manage import SQL_DB
import time

if __name__ == "__main__":
    a = SQL_DB()
    d = a.SQL_SELECT(['sub_end_date', 'chrome_dir_path'], groups_query=False, where_cond='sub_status=1')

    change_sub_status = ''
    for rec in d :
        if time.time() > time.mktime(time.strptime(rec['sub_end_date'], "%Y-%m-%d")) :
            change_sub_status += "chrome_dir_path = " + rec['chrome_dir_path'] + ' or '
    change_sub_status = change_sub_status[ : len(change_sub_status) - 4]

    a.SQL_UPDATE('sub_status=0', change_sub_status)  