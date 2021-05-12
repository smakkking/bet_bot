from logging import config, getLogger
import time
from multiprocessing import Process, Queue
import sys
import signal
import os
import smtplib

from exe_scripts import load_last_data, \
    all_bet, \
    find_matches_live, \
    find_all_links, \
    check_dogon
from db_manage import relogin_clients, \
    reupdate_subscribe
from global_constants import SERVER_DATA_PATH
import bet_manage
from global_links import GROUP_OFFSET

TIME_WAITsec = 7
CRITICAL_ERRORS_LIMIT = 5
WITHOUT_ERRORS_LIMIT = 5


def send_error_msg(text: str):
    return
    smtpObj = smtplib.SMTP('smtp.mail.ru', 2525)
    smtpObj.starttls()
    smtpObj.login("bet-bot_supp@mail.ru", "JQNeU6merbmdL2e")
    smtpObj.sendmail(
        "bet-bot_supp@mail.ru",
        "bet-bot_supp@mail.ru",
        text
    )
    smtpObj.quit()


def clear_fields(DATA, type: str = ''):

    new_upload_data = bet_manage.read_groups()
    for key in GROUP_OFFSET.keys():
        DATA[key]['coupon'].dogon.extend(new_upload_data[key]['coupon'].dogon)
        DATA[key]['coupon'].bets.extend(new_upload_data[key]['coupon'].bets)

        if type == 'bets':
            DATA[key]['coupon'].bets = [x for x in DATA[key]['coupon'].bets if
                                        x.id not in DATA[key]['coupon'].delete_id['bets']]
            DATA[key]['text'] = new_upload_data[key]['text']
            if 'bank' in DATA[key].keys():
                DATA[key].pop('bank')

        elif type == 'dogon':
            DATA[key]['coupon'].dogon = [x for x in DATA[key]['coupon'].dogon
                                         if x.id not in DATA[key]['coupon'].delete_id['dogon']]
            DATA[key]['text'] = new_upload_data[key]['text']
            DATA[key]['coupon'].delay = new_upload_data[key]['coupon'].delay

        elif type == '':
            DATA[key]['coupon'].delay = new_upload_data[key]['coupon'].delay

        DATA[key]['parse_bet'] = (DATA[key]['coupon'].bets != [])


def update_db_time(mode='data'):
    UPDATE_DBh = 6
    now = time.localtime(time.time())
    if mode == 'data':
        return now.tm_hour == UPDATE_DBh and now.tm_min == 0 and 20 <= now.tm_sec <= 40
    elif mode == 'bets':
        return now.tm_hour == UPDATE_DBh and now.tm_min == 0 and now.tm_sec <= 10


def db_sycle(pid1, pid2, pid3, pid4):
    try:
        while True:
            if update_db_time():
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
        getLogger("server_data_update").critical(e, exc_info=True)

        send_error_msg("fucked up in reupdate server!")

        os.kill(pid1, signal.SIGCONT)
        os.kill(pid2, signal.SIGCONT)
        os.kill(pid3, signal.SIGCONT)
        os.kill(pid4, signal.SIGCONT)


def lld_sycle(queue, debug=False):
    CRITICAL_ERRORS_COUNTER = 0
    WIHTOUT_CRITICAL_ERRORS = 0

    while True:
        try:
            t = load_last_data.main(queue)
            if t:
                DATA = find_all_links.main(t)

                queue.put(1, block=True)
                clear_fields(DATA)
                bet_manage.write_groups(DATA)
                queue.get()

            if debug:
                print("lld executed")
                break

            time.sleep(TIME_WAITsec * 2)

            WIHTOUT_CRITICAL_ERRORS += 1
            if WIHTOUT_CRITICAL_ERRORS == WITHOUT_ERRORS_LIMIT:
                CRITICAL_ERRORS_COUNTER = 0
                WIHTOUT_CRITICAL_ERRORS = 0

        except KeyboardInterrupt:
            break
        except Exception as e:

            if debug:
                raise e

            getLogger("load_last_data").critical(e, exc_info=True)
            if queue.full():
                queue.get()
            time.sleep(TIME_WAITsec)

            CRITICAL_ERRORS_COUNTER += 1
            WIHTOUT_CRITICAL_ERRORS = 0

            if CRITICAL_ERRORS_COUNTER == CRITICAL_ERRORS_LIMIT:
                send_error_msg("long critical error in load_last_data!")


def fml_sycle(debug, check_d_queue):
    CRITICAL_ERRORS_COUNTER = 0
    WIHTOUT_CRITICAL_ERRORS = 0

    while True:
        try:
            check_d_queue.put(1, block=True)
            find_matches_live.main()
            check_d_queue.get()

            
            if debug:
                print("fml executed")
                break

            time.sleep(2 * TIME_WAITsec)

            WIHTOUT_CRITICAL_ERRORS += 1
            if WIHTOUT_CRITICAL_ERRORS == WITHOUT_ERRORS_LIMIT:
                CRITICAL_ERRORS_COUNTER = 0
                WIHTOUT_CRITICAL_ERRORS = 0
        except KeyboardInterrupt:
            break
        except Exception as e:

            if check_d_queue.full():
                check_d_queue.get()

            if debug:
                raise e

            getLogger("find_matches_live").critical(e, exc_info=True)

            CRITICAL_ERRORS_COUNTER += 1
            WIHTOUT_CRITICAL_ERRORS = 0

            if CRITICAL_ERRORS_COUNTER == CRITICAL_ERRORS_LIMIT:
                send_error_msg("long critical error in find_matches_live!")


def allb_sycle(queue, debug=False):
    CRITICAL_ERRORS_COUNTER = 0
    WIHTOUT_CRITICAL_ERRORS = 0

    while True:
        try:
            queue.put(1, block=True)
            DATA = bet_manage.read_groups()
            queue.get()

            # очищение delay
            if update_db_time(mode='bets'):
                for key in GROUP_OFFSET.keys():
                    DATA[key]['coupon'].delay = []
                queue.put(1, block=True)
                bet_manage.write_groups(DATA)
                queue.get()
                continue

            for x in DATA.keys():
                DATA[x]['coupon'].dogon = []
            DATA = all_bet.main(DATA)

            if DATA:
                queue.put(1, block=True)
                clear_fields(DATA, type='bets')
                bet_manage.write_groups(DATA)
                queue.get()

            if debug:
                print("allb executed")
                break

            WIHTOUT_CRITICAL_ERRORS += 1
            if WIHTOUT_CRITICAL_ERRORS == WITHOUT_ERRORS_LIMIT:
                CRITICAL_ERRORS_COUNTER = 0
                WIHTOUT_CRITICAL_ERRORS = 0

        except KeyboardInterrupt:
            break
        except Exception as e:

            if debug:
                raise e

            getLogger("all_bet").critical(e, exc_info=True)
            if queue.full():
                queue.get()

            time.sleep(TIME_WAITsec)

            CRITICAL_ERRORS_COUNTER += 1
            WIHTOUT_CRITICAL_ERRORS = 0

            if CRITICAL_ERRORS_COUNTER == CRITICAL_ERRORS_LIMIT:
                send_error_msg("long critical error in all_bet!")


def checkd_sycle(queue, queue2, debug=False):
    CRITICAL_ERRORS_COUNTER = 0
    WIHTOUT_CRITICAL_ERRORS = 0

    while True:
        try:
            # реализовано через задницу, но обеспечивает качественную работу поиска матче  
            queue2.put(1, block=True)          
            queue.put(1, block=True)
            DATA = bet_manage.read_groups()
            queue.get()
            

            for x in DATA.keys():
                DATA[x]['coupon'].bets = []

            DATA = check_dogon.main(DATA)

            if DATA: 
                queue.put(1, block=True)
                clear_fields(DATA, type='dogon')
                bet_manage.write_groups(DATA)
                queue.get()

            queue2.get()

            if debug:
                print("checkd executed")
                break

            WIHTOUT_CRITICAL_ERRORS += 1
            if WIHTOUT_CRITICAL_ERRORS == WITHOUT_ERRORS_LIMIT:
                CRITICAL_ERRORS_COUNTER = 0
                WIHTOUT_CRITICAL_ERRORS = 0

        except KeyboardInterrupt:
            break
        except Exception as e:

            if debug:
                raise e

            getLogger("check_dogon").critical(e, exc_info=True)
            if queue.full():
                queue.get()
            
            if queue2.full():
                queue2.get()

            CRITICAL_ERRORS_COUNTER += 1
            WIHTOUT_CRITICAL_ERRORS = 0

            if CRITICAL_ERRORS_COUNTER == CRITICAL_ERRORS_LIMIT:
                send_error_msg("long critical error in check_dogon!")


if __name__ == "__main__":
    dictLogConfig = {
        "version": 1,
        "handlers": {
            "script": {
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": SERVER_DATA_PATH + "logs/script_info.log"
            },
            "groups": {
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": SERVER_DATA_PATH + 'logs/groups.log'
            },
            "bets": {
                "class": "logging.FileHandler",
                "formatter": "bets_formater",
                "filename": SERVER_DATA_PATH + "logs/bet_info.log"
            }
        },
        "loggers": {
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
            "server_data_update": {
                "handlers": ["script"],
                "level": "INFO",
            },
        },
        "formatters": {
            "myFormatter": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "bets_formater": {
                "format": "%(asctime)s - %(levelname)s\n%(message)s"
            }
        }
    }
    for key in GROUP_OFFSET.keys():
        dictLogConfig['loggers'][key] = {
            "handlers": ["groups"],
            "level": "INFO",
        }
    config.dictConfig(dictLogConfig)
    debug = '-debug' in sys.argv

    all_posts_json_qu = Queue(maxsize=1)
    qu2 = Queue(maxsize=1)

    
    proc2 = Process(target=lld_sycle, args=(all_posts_json_qu, debug, ))
    proc3 = Process(target=allb_sycle, args=(all_posts_json_qu, debug, ))
    proc4 = Process(target=checkd_sycle, args=(all_posts_json_qu, qu2, debug, ))

    proc2.start()
    proc3.start()
    proc4.start()

    proc1 = Process(target=fml_sycle, args=(debug, qu2))
    proc1.start()

    if not debug:
        proc5 = Process(target=db_sycle, args=(
            proc1.pid, proc2.pid, proc3.pid, proc4.pid, ))
        proc5.start()
        proc5.join()
