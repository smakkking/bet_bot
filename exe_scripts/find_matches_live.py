import time
import json
import logging

from datetime import datetime, timedelta
from dateutil import parser

from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH

def main(main_logger=None) :
    if main_logger :
        now = time.time()

    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            with open(SERVER_DATA_PATH + v.NAME + '.json', 'r', encoding="utf-8") as f:
                x = json.load(f)
            try :
                if datetime.now() - parser.parse(x['last_update_all']) >= timedelta(hours=v.MATCHES_UPDATE_TIMEh) :
                    x['events'] = v.find_bet(x['events'], update_all=True)
                    x['last_update_all'] = datetime.now().isoformat()
                    x['last_update_live'] = datetime.now().isoformat()
                elif datetime.now() - parser.parse(x['last_update_live']) >= timedelta(hours=v.LIVE_MATCHES_UPDATE_TIMEh) :
                    x['events'] = v.find_bet(x['events'], update_live=True)
                    x['last_update_live'] = datetime.now().isoformat()
            except Exception as e :
                logging.getLogger("find_matches_live").error(v.NAME + " failed because of " + e)

            with open(SERVER_DATA_PATH + v.NAME + '.json', 'w', encoding="utf-8") as f:
                json.dump(x, f, indent=4)

    if main_logger :
        main_logger.info('{0:.2f} spent'.format(time.time() - now))

if __name__ == '__main__':
    while True:
        main()
