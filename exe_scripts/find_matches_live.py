import time
import json

from datetime import datetime, timedelta
from dateutil import parser

from global_constants import BOOKMAKER_OFFSET, MATCHES_UPDATE_TIMEh, SERVER_DATA_PATH

def main(main_logger=None) :
    # TODO переделать на параллельный поиск
    if main_logger :
        now = time.time()

    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            with open(SERVER_DATA_PATH + v.NAME + '.json', 'r', encoding="utf-8") as f:
                x = json.load(f)
            if 'last_update' in x.keys() and \
                    datetime.now() - parser.parse(x['last_update']) < timedelta(hours=MATCHES_UPDATE_TIMEh) :
                continue
            else :
                final = {
                    'events' : v.find_bet(),
                    'last_update' : datetime.now().isoformat(),
                }
                with open(SERVER_DATA_PATH + v.NAME + '.json', 'w', encoding="utf-8") as f:
                    json.dump(final, f, indent=4)

    if main_logger :
        main_logger.info('{0:.2f} spent on find matches links'.format(time.time() - now))

if __name__ == '__main__':
    main()
