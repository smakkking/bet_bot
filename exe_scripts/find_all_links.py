from multiprocessing import Pool
import functools
import logging
import json

from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET, SERVER_DATA_PATH
import bet_manage

def find_all_links(DATA, bk_events, key_g) :
    group = DATA[key_g]
    if group['coupon'].type == 'ordn' :
        for stavka in group['coupon'].bets :
            for key in BOOKMAKER_OFFSET.keys() :
                if BOOKMAKER_OFFSET[key].HAS_API :
                    pass
                elif BOOKMAKER_OFFSET[key].TAKES_MATCHES_LIVE :
                    pass
                else :
                    if key in stavka.bk_links and stavka.bk_links[key] is not None:
                        continue
                    stavka.set_bk_link(key, BOOKMAKER_OFFSET[key].get_info(stavka, bk_events[key]))
                    if stavka.bk_links[key] is None:
                        logging.getLogger("find_all_links").info(f"{key} has no info for {key_g}")
    else :
        # не умеет работать с системой ставок(когда одновременно), а может это и не нужно???
        pass
    return (key_g, DATA[key_g])

def main(DATA: dict) :

    bk_events = {}
    for key in BOOKMAKER_OFFSET.keys():
        bet_manage.file_is_available(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json')
        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json', 'r', encoding="utf-8") as f:
            dat = json.load(f)
            bk_events[key] = dat['events']


    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(find_all_links, DATA, bk_events), GROUP_OFFSET.keys()))

    return DATA


