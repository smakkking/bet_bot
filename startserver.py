from logging import config
import time
from multiprocessing import Process
import sys

from exe_scripts import load_last_data, \
                        all_bet, \
                        find_matches_live, \
                        find_all_links, \
                        check_dogon
from db_manage import   relogin_clients, \
                        reupdate_subscribe
from global_constants import BET_PROJECT_ROOT, GROUP_OFFSET
import bet_manage


def update_db_time() :
    UPDATE_DBh = 5
    now = time.localtime(time.time())
    return now.tm_hour == UPDATE_DBh and now.tm_min == 0 and now.tm_sec <= 30


def db_sycle(debug=False) :

    while True :
        if update_db_time() :
            reupdate_subscribe.main()
            relogin_clients.main()
        if debug:
            print("db executed")
            time.sleep(20)


def lld_sycle(debug=False) :
    TIME_WAITsec = 15
    while True :
        if update_db_time():
            print('i sleep')
            time.sleep(60)

        t = load_last_data.main()
        DATA = find_all_links.main(t)

        bet_manage.write_groups(DATA)
        time.sleep(TIME_WAITsec)

        if debug:
            print("lld executed")


def fml_sycle(debug=False):
    while True :
        if update_db_time():
            print('i sleep')
            time.sleep(60)

        find_matches_live.main()

        if debug:
            print("fml executed")
            time.sleep(20)


def allb_sycle(debug=False):
    while True:
        if update_db_time():
            print('i sleep')
            time.sleep(60)

        DATA = bet_manage.read_groups()
        bet_manage.write_groups(all_bet.main(DATA))

        if debug:
            print("allb executed")
            time.sleep(20)


def checkd_sycle(debug=False):
    while True :
        if update_db_time():
            print('i sleep')
            time.sleep(60)

        DATA = bet_manage.read_groups()
        bet_manage.write_groups(check_dogon.main(DATA))

        if debug:
            print("checkd executed")
            time.sleep(20)


if __name__ == "__main__" :

    dictLogConfig = {
        "version":1,
        "handlers":{
            "script":{
                "class":"logging.FileHandler",
                "formatter":"myFormatter",
                "filename": BET_PROJECT_ROOT + "exe_scripts/script_info.log"
            },
            "groups":{
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename":BET_PROJECT_ROOT + 'moduls/group_moduls/groups.log'
            },
            "bets":{
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": BET_PROJECT_ROOT + "exe_scripts/bet_info.log"
            }
        },
        "loggers":{
            "load_last_data": {
                "handlers": ["script"],
                "level": "INFO",
            },
            "all_bet": {
                "handlers": ["script"],
                "level": "INFO",
            },
            "find_matches_live": {
                "handlers": ["script"],
                "level": "INFO",
            },
            "find_all_links": {
                "handlers": ["script"],
                "level": "INFO",
            },
            "check_dogon": {
                "handlers": ["script"],
                "level": "INFO",
            },
        },
        "formatters":{
            "myFormatter":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }

    for key in GROUP_OFFSET.keys() :
        dictLogConfig['loggers'][key] = {
            "handlers": ["groups"],
            "level": "INFO",
        }

    config.dictConfig(dictLogConfig)

    linear = '-linear' in sys.argv
    if linear:
        # системные скрипты выполнятются редко
        find_matches_live.main()

        # основные скрипты выполняются постоянно
        GROUP_DATA = load_last_data.main()

        GROUP_DATA = find_all_links.main(GROUP_DATA)

        GROUP_DATA = all_bet.main(GROUP_DATA)

        GROUP_DATA = check_dogon.main(GROUP_DATA)

        bet_manage.write_groups(GROUP_DATA)
    else :
        debug = '-debug' in sys.argv

        proc1 = Process(target=fml_sycle, args=(debug, ))
        proc2 = Process(target=lld_sycle, args=(debug, ))
        proc3 = Process(target=db_sycle, args=(debug, ))
        proc4 = Process(target=allb_sycle, args=(debug, ))
        proc5 = Process(target=checkd_sycle, args=(debug, ))

        proc4.start()
        proc1.start()
        proc2.start()
        proc3.start()
        proc5.start()

        proc4.join()
        proc1.join()
        proc2.join()
        proc3.join()
        proc5.join()
