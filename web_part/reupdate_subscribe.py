from manage import DATABASE_PATH
import sqlite3
from sqlite3 import Error
from moduls.bet_manage import SQL_DB
from datetime import datetime

if __name__ == "__main__":
    # возможно лучше переделать с интерфейсом django
    a = SQL_DB()
    d = a.SQL_SELECT(select_cond=['sub_end_date', 'chrome_dir_path', 'id'], groups_query=False, where_cond='sub_status=1 and bot_status=1')

    change_sub_status = ''
    for rec in d :
        if datetime.today > datetime.strptime(rec['sub_end_date'], "%Y-%m-%d") :
            change_sub_status += "id = " + rec['id'] + ' or '
    change_sub_status = change_sub_status[ : len(change_sub_status) - 4]

    a.SQL_UPDATE(set_cond='sub_status=0', where_cond=change_sub_status)  