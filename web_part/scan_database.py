import sqlite3
from sqlite3 import Error
from moduls.bet_manage import GROUP_OFFSET
from manage import DATABASE_PATH

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error:
        pass
    return connection

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error:
        pass

def SQL_request(connection, *args) :
    select_users = "SELECT\n"

    for arg in args :
        select_users += ', ' + arg
    for group in GROUP_OFFSET.values() :
        select_users += ', ' + group.NAME

    select_users = select_users.replace(',', '', 1)
    select_users += """\nFROM UserDataManagment_standartuser WHERE subscribe_status = 1"""

    users = execute_read_query(connection, select_users)
    result = []

    for user in users:
        dic = {}
        for i in range(len(args)) :
            dic[args[i]] = user[i]
        p = []
        i = 0
        for value in GROUP_OFFSET.values() :
            if user[i + len(args)] :
                p.append(value.NAME)
            i += 1
        dic['groups'] = p
        result.append(dic)

    return result

def main() :
    connection = create_connection(DATABASE_PATH)
    # возвращает list из записей вида
    # {
    #   'chrome_id' : str
    #   'bkm' : str
    #   'groups' : list
    # }
    # возможно нужно добавить сюда пароли(но это доп время на обработку)


    # Что добавить в поиск : сумму ставки
    return SQL_request(connection, 'chrome_dir_path', 'bookmaker')
