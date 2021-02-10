import json
import logging

from datetime import datetime, timedelta
from dateutil import parser

from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH
import bet_manage


def main() :
    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            try :
                bet_manage.file_is_available(SERVER_DATA_PATH + v.NAME + '/matches.json')
                with open(SERVER_DATA_PATH + v.NAME + '/matches.json', 'r', encoding="utf-8") as f:
                    x = json.load(f)
            except :
                x = {}
            try:
                if datetime.now() - parser.parse(x['last_update']) >= timedelta(minutes=v.LIVE_MATCHES_UPDATE_TIMEm):
                    x['events'] = v.find_bet()
                    x['last_update'] = datetime.now().isoformat()
                else :
                    continue
            except AssertionError as e:
                logging.getLogger("find_matches_live").error(v.NAME + " failed")
                continue

            logging.getLogger("find_matches_live").info(v.NAME + " ended normally")

            bet_manage.file_is_available(SERVER_DATA_PATH + v.NAME + '/matches.json')
            with open(SERVER_DATA_PATH + v.NAME + '/matches.json', 'w', encoding="utf-8") as f:
                json.dump(x, f, indent=4)

if __name__ == '__main__':
    main()
