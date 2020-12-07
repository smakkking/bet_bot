import time

from global_constants import BOOKMAKER_OFFSET

def main(main_logger=None) :

    if main_logger :
        now = time.time()

    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            v.find_bet()

    if main_logger :
        main_logger.info('{0:.2f} spent on find matches links'.format(time.time() - now))