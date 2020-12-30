from logging import config
import logging
import json

from exe_scripts import load_last_data, \
                        scan_database, \
                        all_bet, \
                        find_matches_live, \
                        find_all_links, \
                        check_dogon
from global_constants import BET_PROJECT_ROOT, ALL_POSTS_JSON_PATH, GROUP_OFFSET

# осуществляет непосредственно ставочный процесс для всех клиентов
# работает круглосуточно

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
            "relogin_live":{
                "handlers":["script"],
                "level":"INFO",
            },
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
            "bet_status": {
                "handlers": ["bets"],
                "level": "INFO",
            }
        },
        "formatters":{
            "myFormatter":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }
    config.dictConfig(dictLogConfig)

    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        GROUP_DATA = json.load(last_posts_json)

    # системные скрипты выполнятются редко
    find_matches_live.main(logging.getLogger("find_matches_live"))

    # основные скрипты выполняются постоянно
    GROUP_DATA = load_last_data.main(logging.getLogger("load_last_data"))

    GROUP_DATA = find_all_links.main(GROUP_DATA, logging.getLogger("find_all_links"))

    GROUP_DATA = all_bet.main(GROUP_DATA, scan_database.main(), logging.getLogger("all_bet"))

    GROUP_DATA = check_dogon.main(GROUP_DATA, logging.getLogger("check_dogon"))

    for x in GROUP_DATA.keys() :
        GROUP_DATA[x]['coupon'] = GROUP_DATA[x]['coupon'].__json_repr__()
    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(GROUP_DATA, last_posts_json, indent=4)



