import json
import logging
import time

from datetime import datetime, timedelta
from dateutil import parser

from global_constants import SERVER_DATA_PATH
from global_links import BOOKMAKER_OFFSET
import bet_manage


def main() :
    # идеальный пример взаимодействия интерфейсов
    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            with open(SERVER_DATA_PATH + v.NAME + '/matches.json', 'r', encoding="utf-8") as f:
                    x = json.load(f)

            if datetime.now() - parser.parse(x['last_update']) >= timedelta(minutes=v.LIVE_MATCHES_UPDATE_TIMEm):
                x['events'] = v.find_bet(x['events'])
                x['last_update'] = datetime.now().isoformat()
            else :
                continue

            bet_manage.file_is_available(SERVER_DATA_PATH + v.NAME + '/matches.json')
            with open(SERVER_DATA_PATH + v.NAME + '/matches.json', 'w', encoding="utf-8") as f:
                json.dump(x, f, indent=4)


if __name__ == '__main__':
    main()
