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
            try :
                if x == {} :
                    x['events'] = v.find_bet([], update_all=True)
                    x['last_update_all'] = datetime.now().isoformat()
                    x['last_update_live'] = datetime.now().isoformat()
                elif datetime.now() - parser.parse(x['last_update_all']) >= timedelta(hours=v.MATCHES_UPDATE_TIMEh) :
                    x['events'] = v.find_bet(x['events'], update_all=True)
                    x['last_update_all'] = datetime.now().isoformat()
                    x['last_update_live'] = datetime.now().isoformat()
                elif datetime.now() - parser.parse(x['last_update_live']) >= timedelta(minutes=v.LIVE_MATCHES_UPDATE_TIMEm) :
                    x['events'] = v.find_bet(x['events'], update_live=True)
                    x['last_update_live'] = datetime.now().isoformat()
            except Exception as e :
                logging.getLogger("find_matches_live").error(v.NAME + " failed because of " + str(e))

            bet_manage.file_is_available(SERVER_DATA_PATH + v.NAME + '/matches.json')
            with open(SERVER_DATA_PATH + v.NAME + '/matches.json', 'w', encoding="utf-8") as f:
                json.dump(x, f, indent=4)

if __name__ == '__main__':
    while True:
        main()
