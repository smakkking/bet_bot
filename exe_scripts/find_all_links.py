import json
from multiprocessing import Pool
import functools
import time

from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET, SERVER_DATA_PATH

def find_all_links(DATA, key_g) :
    group = DATA[key_g]
    if group['parse_bet'] :
        if group['coupon'].type == 'ordn' :
            for stavka in group['coupon'].bets :
                if stavka.bk_links != {} :
                    continue
                for key in BOOKMAKER_OFFSET.keys() :
                    if BOOKMAKER_OFFSET[key].HAS_API :
                        pass
                    elif BOOKMAKER_OFFSET[key].TAKES_MATCHES_LIVE :
                        # из словаря получается объект ставки
                        # должна вызываться функция find_bet
                        # подразумеваем, что в этой функции в экземпляр класса Stakva() устанавливается ссылка на матч
                        # очень возможно, что лучше перенести создание браузера в find_bet
                        pass
                    else :
                        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '.json', 'r', encoding="utf-8") as f :
                            dat = json.load(f)
                            dat = dat['events']
                        for x in dat :
                            # совпадает ли название матча
                            if stavka.match_title.find(x['team1']) >= 0 and stavka.match_title.find(x['team2']) >= 0 :
                                stavka.set_bk_link(key, x['link'])
        else :
            # не умеет работать с системой ставок(когда одновременно)
            pass
    return (key_g, DATA[key_g])

def main(DATA: dict, main_logger=None) :
    if main_logger :
        now = time.time()
    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(find_all_links, DATA), GROUP_OFFSET.keys()))
    if main_logger:
        main_logger.info('{0:.2f} spent on finding links for all bets'.format(time.time() - now))
    return DATA

