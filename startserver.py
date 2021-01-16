from logging import config
import time
from multiprocessing import Process

from exe_scripts import load_last_data, \
                        all_bet, \
                        find_matches_live, \
                        find_all_links, \
                        check_dogon
from db_manage import   relogin_clients, \
                        reupdate_subscribe
from global_constants import BET_PROJECT_ROOT, GROUP_OFFSET
import bet_manage
# осуществляет непосредственно ставочный процесс для всех клиентов
# работает круглосуточно

def db_sycle() :
    # нужно, чтобы при срабатывании этих скриптов все остальные прекратили свою работу
    # как это сделать?
    UPDATE_DBh = 4

    while True :
        now = time.gmtime(time.time())
        if now.tm_hour == UPDATE_DBh and now.tm_min == 0 and now.tm_sec <= 20:
            reupdate_subscribe.main()
            relogin_clients.main()

def lld_sycle() :
    TIME_WAITsec = 15
    while True :
        t = load_last_data.main()
        DATA = find_all_links.main(t)

        bet_manage.write_groups(DATA)
        print("data_loaded. I'm waiting")
        time.sleep(TIME_WAITsec)

def fml_sycle():
    while True :
        find_matches_live.main()

def allb_sycle():
    while True:
        DATA = bet_manage.read_groups()
        bet_manage.write_groups(all_bet.main(DATA))

def checkd_sycle():
    while True :
        DATA = bet_manage.read_groups()
        bet_manage.write_groups(check_dogon.main(DATA))


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
    """
    while True :
        # системные скрипты выполнятются редко
        find_matches_live.main()

        # основные скрипты выполняются постоянно
        GROUP_DATA = load_last_data.main()

        GROUP_DATA = find_all_links.main(GROUP_DATA)

        GROUP_DATA = all_bet.main(GROUP_DATA)

        GROUP_DATA = check_dogon.main(GROUP_DATA)

        bet_manage.write_groups(GROUP_DATA)
    """






