import sqlite3
from sqlite3 import Error
from moduls.bet_manage import GROUP_OFFSET, SQL_DB
from manage import DATABASE_PATH

def main() :
    a = SQL_DB()
    b = a.SQL_SELECT(['chrome_dir_path', 'bookmaker', 'bet_summ', 'id'], where_cond='sub_status=1 and bot_status=1', groups_query=True)
    return b

if __name__ == "__main__":
    print(main())