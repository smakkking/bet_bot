from logging import config, getLogger
import time
from multiprocessing import Process, Queue
import sys
import signal
import os
import random

from exe_scripts import load_last_data, \
                        all_bet, \
                        find_matches_live, \
                        find_all_links, \
                        check_dogon
from db_manage import   relogin_clients, \
                        reupdate_subscribe
from global_constants import GROUP_OFFSET, SERVER_DATA_PATH
import bet_manage

TIME_WAITsec = 5

def update_db_time() :
    UPDATE_DBh = 7
    now = time.localtime(time.time())
    return now.tm_hour == UPDATE_DBh and now.tm_min == 0 and now.tm_sec <= 10


def db_sycle(pid1, pid2, pid3, pid4) :
    try :
        while True :
            if update_db_time() :
                os.kill(pid1, signal.SIGSTOP)
                os.kill(pid2, signal.SIGSTOP)
                os.kill(pid3, signal.SIGSTOP)
                os.kill(pid4, signal.SIGSTOP)

                relogin_clients.main()
                reupdate_subscribe.main()

                os.kill(pid1, signal.SIGCONT)
                os.kill(pid2, signal.SIGCONT)
                os.kill(pid3, signal.SIGCONT)
                os.kill(pid4, signal.SIGCONT)

                getLogger("server_data_update").info("ended normally")
    except KeyboardInterrupt:
        return
    except Exception as e:
        getLogger("server_data_update").critical(f"stopped with {e}")
        os.kill(pid1, signal.SIGCONT)
        os.kill(pid2, signal.SIGCONT)
        os.kill(pid3, signal.SIGCONT)
        os.kill(pid4, signal.SIGCONT)



def lld_sycle(queue, debug=False) :
    while True :
        try:
            t = load_last_data.main(queue)
            DATA = find_all_links.main(t)

            queue.put(1, block=True)

            new_upload_data = bet_manage.read_groups()
            for key in GROUP_OFFSET.keys():
                try:
                    DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)
                    DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)
                    DATA[key]['coupon'].delay.extend(new_upload_data[key]['coupon'].delay)
                except KeyError:
                    continue
            DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])
            bet_manage.write_groups(DATA)

            queue.get()

            if debug:
                print("lld executed")
                break
            time.sleep(TIME_WAITsec * 2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            getLogger("load_last_data").critical(f"stopped with {e}")
            if queue.full():
                queue.get()
            if debug:
                raise e
            time.sleep(TIME_WAITsec)


def fml_sycle(debug=False):
    while True :
        try:
            duration = time.time()

            find_matches_live.main()
            if debug:
                print("fml executed")
                break

            if time.time() - duration < 5:
                time.sleep(TIME_WAITsec)

        except KeyboardInterrupt:
            break
        except Exception as e:
            getLogger("find_matches_live").critical(f"stopped with {e}")
            if debug:
                raise e


def allb_sycle(queue, debug=False):
    while True:
        try:
            duration = time.time()

            queue.put(1, block=True)
            DATA = bet_manage.read_groups()
            queue.get()

            for x in DATA.keys():
                DATA[x]['coupon'].dogon = []
            DATA = all_bet.main(DATA)

            if time.time() - duration < 3:
                time.sleep(TIME_WAITsec)
            else:
                getLogger("all_bet").info("ended normally")


            queue.put(1, block=True)

            new_upload_data = bet_manage.read_groups()
            for key in GROUP_OFFSET.keys():
                DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)
                DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)
                DATA[key]['coupon'].bets = [x for x in DATA[key]['coupon'].bets if
                                             x.id not in DATA[key]['coupon'].delete_id['bets']]


                # нужно ли обрабатывать
                DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])
                DATA[key]['text'] = new_upload_data[key]['text']
            bet_manage.write_groups(DATA)

            queue.get()

            if debug:
                print("allb executed")
                break

        except KeyboardInterrupt:
            break
        except Exception as e:
            getLogger("all_bet").critical(f"stopped with {e}")
            if queue.full():
                queue.get()
            if debug:
                raise e
            time.sleep(TIME_WAITsec)


def checkd_sycle(queue, debug=False):
    while True :
        try:
            queue.put(1, block=True)
            DATA = bet_manage.read_groups()
            queue.get()

            for x in DATA.keys():
                DATA[x]['coupon'].bets = []

            DATA = check_dogon.main(DATA)

            queue.put(1, block=True)

            new_upload_data = bet_manage.read_groups()
            for key in GROUP_OFFSET.keys() :
                DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)
                DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)
                DATA[key]['coupon'].dogon = [x for x in DATA[key]['coupon'].dogon
                                             if x.id not in DATA[key]['coupon'].delete_id['dogon']]
                # нужно ли обрабатывать
                DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])
                DATA[key]['text'] = new_upload_data[key]['text']
            bet_manage.write_groups(DATA)

            queue.get()

            if debug:
                print("checkd executed")
                break
            else:
                time.sleep(60)

        except KeyboardInterrupt:
            break
        except Exception as e:
            getLogger("check_dogon").critical(f"stopped with {e}")

            if queue.full():
                queue.get()

            if debug:
                raise e
            time.sleep(TIME_WAITsec)


if __name__ == "__main__" :
    dictLogConfig = {
        "version":1,
        "handlers":{
            "script":{
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": SERVER_DATA_PATH + "logs/script_info.log"
            },
            "groups":{
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": SERVER_DATA_PATH + 'logs/groups.log'
            },
            "bets":{
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": SERVER_DATA_PATH + "logs/bet_info.log"
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
            "created_bets": {
                "handlers": ["bets"],
                "level": "INFO",
            },
            "server_data_update" : {
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
            # больше не работает
            GROUP_DATA = check_dogon.main(GROUP_DATA)
            if debug:
                print("checkd executed")

            bet_manage.write_groups(GROUP_DATA)

            if update_db_time():
                reupdate_subscribe.main()
                relogin_clients.main()
    else :
        debug = '-debug' in sys.argv

        all_posts_json_qu = Queue(maxsize=1)

        proc1 = Process(target=fml_sycle, args=(debug, ))
        proc2 = Process(target=lld_sycle, args=(all_posts_json_qu, debug, ))
        proc3 = Process(target=allb_sycle, args=(all_posts_json_qu, debug, ))
        proc4 = Process(target=checkd_sycle, args=(all_posts_json_qu, debug, ))

        proc1.start()
        proc2.start()
        proc3.start()
        proc4.start()


        if not debug :
            proc5 = Process(target=db_sycle, args=(proc1.pid, proc2.pid, proc3.pid, proc4.pid))
            proc5.start()
            proc5.join()
            pass

        #proc1.join()
        #proc2.join()
        #proc3.join()
        #proc4.join()
