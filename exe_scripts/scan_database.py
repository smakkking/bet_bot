from bet_manage import SQL_DB


def main() :
    a = SQL_DB()
    b = a.SQL_SELECT(
        ['chrome_dir_path', 'bookmaker', 'bet_summ', 'id', 'bookmaker_login', 'bookmaker_password'],
        where_cond='sub_status=1 and bot_status=1',
        groups_query=True
    )
    return b

if __name__ == "__main__":
    print(main())