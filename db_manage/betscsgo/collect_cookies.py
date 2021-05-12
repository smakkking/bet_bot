import json
import sqlite3
import sys

from global_constants import SERVER_DATA_PATH

BASE = '/home/smaking/.mozilla/firefox/'
PROFILES_LIST = [
    'rwythdx5.default-release', # добавить сюда default-release профиль
    'laro57pv.proxy_0',
    'pu9afky9.proxy_1',
]

if '-collect' in sys.argv:
    with open(SERVER_DATA_PATH + 'betscsgo/proxy_table.json') as f:
        proxy_data = json.load(f)

    for pr in PROFILES_LIST:
        # обрабатывать отдельно default-release профиль
        # куки будут выводиться в отдельный файл main_cookies.txt
        # i -= 1

        i = PROFILES_LIST.index(pr) - 1

        conn = sqlite3.connect(BASE + pr + '/cookies.sqlite')
        cur = conn.cursor()

        cur.execute("select * from main.moz_cookies where name == 'cf_clearance'")
        all_results = cur.fetchall()

        cook_arr = []
        for cookies in all_results:
            if cookies[4] == '.betscsgo.in':
                s = {
                    'name': 'cf_clearance',
                    'value': cookies[3],
                    'domain': 'betscsgo.in'
                }
            elif cookies[4] == '.betsdota2.fun':
                s = {
                    'name': 'cf_clearance',
                    'value': cookies[3],
                    'domain': 'betsdota2.fun'
                }
            if s:
                cook_arr.append(s)

        if pr == 'rwythdx5.default-release':
            with open('main_cookies.json', 'w') as f:
                json.dump(cook_arr, f, indent=4)
        else:
            proxy_data[i]['cookies'] = cook_arr

        conn.close()

    with open(SERVER_DATA_PATH + 'betscsgo/proxy_table.json', 'w') as f:
        json.dump(proxy_data, f, indent=4)

elif '-delete' in sys.argv:
    for pr in PROFILES_LIST:
        conn = sqlite3.connect(BASE + pr + '/cookies.sqlite')
        cur = conn.cursor()

        cur.execute("DELETE FROM main.moz_cookies WHERE name == 'cf_clearance'")

        conn.commit()
        conn.close()
