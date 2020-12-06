import time

from global_constants import BOOKMAKER_OFFSET

def main(debug=False) :

    if debug :
        now = time.time()

    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATCHES_LIVE :
            v.find_bet()

    if debug :
        print('{0:.2f} spent on find matches links'.format(time.time() - now))