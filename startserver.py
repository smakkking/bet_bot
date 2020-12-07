from logging import config
import logging

from exe_scripts import relogin_live, load_last_data, scan_database, all_bet, find_matches_live
from global_constants import BET_PROJECT_ROOT

# осуществляет непосредственно ставочный процесс для всех клиентов
# работает круглосуточно

if __name__ == "__main__" :

    dictLogConfig = {
        "version":1,
        "handlers":{
            "fileHandler":{
                "class":"logging.FileHandler",
                "formatter":"myFormatter",
                "filename": BET_PROJECT_ROOT + "exe_scripts/script_info.log"
            }
        },
        "loggers":{
            "relogin_live":{
                "handlers":["fileHandler"],
                "level":"INFO",
            },
            "load_last_data": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            },
            "scan_database": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            },
            "all_bet": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            },
            "find_matches_live": {
                "handlers": ["fileHandler"],
                "level": "INFO",
            },
        },
        "formatters":{
            "myFormatter":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }

    config.dictConfig(dictLogConfig)

    # выполнятются редко
    find_matches_live.main(logging.getLogger("find_matches_live"))
    relogin_live.main(logging.getLogger("relogin_live"))

    # выполняются постоянно
    #load_last_data.main(logging.getLogger("load_last_data"))
    client_data = scan_database.main()
    all_bet.main(client_data, logging.getLogger("all_bet"))



