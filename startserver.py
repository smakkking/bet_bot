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
from global_constants import BET_PROJECT_ROOT, GROUP_OFFSET, ALL_POSTS_JSON_PATH
import bet_manage


def update_db_time() :
    UPDATE_DBh = 7
    now = time.localtime(time.time())
    return now.tm_hour == UPDATE_DBh and now.tm_min == 0 and now.tm_sec <= 30


def db_sycle(debug=False) :
    try :
        while True :
            if update_db_time() :
                reupdate_subscribe.main()
                relogin_clients.main()
            if debug:
                print("db executed")
                time.sleep(20)
    except Exception as e:
        print(f"db_sycle ended: {e}")
        raise e

def lld_sycle(debug=False) :
    TIME_WAITsec = 15
    try :
        while True :
            if update_db_time():
                print('i sleep')
                time.sleep(60)

            t = load_last_data.main()
            DATA = find_all_links.main(t)

            # предотвращает потерю данных
            # мы знаем, что старые данные в DATA.coupon.bets и DATA.coupon.dogon удалены
            bet_manage.file_is_available(ALL_POSTS_JSON_PATH)
            with open(ALL_POSTS_JSON_PATH, 'r') as f:
                new_upload_data = bet_manage.read_groups()
                for key in GROUP_OFFSET.keys() :
                    DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)
                    DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)
                DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])
                bet_manage.write_groups(DATA)

            time.sleep(TIME_WAITsec)
            if debug:
                print("lld executed")
    except Exception as e:
        print(f"lld_sycle ended: {e}")
        raise e

def fml_sycle(debug=False):
    try :
        while True :
            if update_db_time():
                print('i sleep')
                time.sleep(60)

            find_matches_live.main()

            if debug:
                print("fml executed")
                time.sleep(20)
    except Exception as e:
        print(f"fml_sycle ended: {e}")
        raise e

def allb_sycle(debug=False):
    try:
        while True:
            if update_db_time():
                print('i sleep')
                time.sleep(60)

            bet_manage.file_is_available(ALL_POSTS_JSON_PATH)
            DATA = bet_manage.read_groups()

            for x in DATA.keys():
                DATA[x]['coupon'].dogon = []

            DATA = all_bet.main(DATA)

            # предотвращает потерю данных
            bet_manage.file_is_available(ALL_POSTS_JSON_PATH)
            with open(ALL_POSTS_JSON_PATH, 'r') as f:
                new_upload_data = bet_manage.read_groups()

                for key in GROUP_OFFSET.keys():
                    DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)

                    for x in DATA[key]['coupon'].bets:
                        try :
                            pos = new_upload_data[key]['coupon'].bets.index(x)
                        except ValueError:
                            continue
                        del new_upload_data[key]['coupon'].bets[pos]
                    DATA[key]['coupon'].bets = new_upload_data[key]['coupon'].bets
                    # нужно ли обрабатывать
                    DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])
                bet_manage.write_groups(DATA)

            if debug:
                print("allb executed")
                time.sleep(20)
    except Exception as e:
        print(f"allb_sycle ended: {e}")
        raise e

def checkd_sycle(debug=False):
    try:
        while True :
            if update_db_time():
                print('i sleep')
                time.sleep(60)

            bet_manage.file_is_available(ALL_POSTS_JSON_PATH)
            DATA = bet_manage.read_groups()

            for x in DATA.keys():
                DATA[x]['coupon'].bets = []

            DATA = check_dogon.main(DATA)

            bet_manage.file_is_available(ALL_POSTS_JSON_PATH)
            with open(ALL_POSTS_JSON_PATH, 'r') as f:
                new_upload_data = bet_manage.read_groups()

                for key in GROUP_OFFSET.keys() :
                    DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)

                    for x in DATA[key]['coupon'].dogon:
                        try :
                            pos = new_upload_data[key]['coupon'].dogon.index(x)
                        except ValueError:
                            continue
                        del new_upload_data[key]['coupon'].dogon[pos]

                    DATA[key]['coupon'].dogon = new_upload_data[key]['coupon'].dogon

                    # нужно ли обрабатывать
                    DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])

                bet_manage.write_groups(DATA)

            if debug:
                print("checkd executed")
                time.sleep(20)
    except Exception as e:
        print(f"checkd_sycle ended: {e}")
        raise e

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

    if '-linear' in sys.argv:

        debug = '-debug' in sys.argv

        while True :
            find_matches_live.main()
            if debug:
                print("fml executed")

            # основные скрипты выполняются постоянно
            GROUP_DATA = load_last_data.main()
            if debug:
                print("lld executed")

            GROUP_DATA = find_all_links.main(GROUP_DATA)
            if debug:
                print("fal executed")

            GROUP_DATA = all_bet.main(GROUP_DATA)
            if debug:
                print("allb executed")

            GROUP_DATA = check_dogon.main(GROUP_DATA)
            if debug:
                print("checkd executed")

            bet_manage.write_groups(GROUP_DATA)

            if update_db_time():
                reupdate_subscribe.main()
                relogin_clients.main()
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
