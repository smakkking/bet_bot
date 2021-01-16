import json
from multiprocessing import Pool
import functools
import bet_manage

from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET, ALL_POSTS_JSON_PATH

def find_all_links(DATA, key_g) :
    group = DATA[key_g]
    if group['parse_bet'] :
        if group['coupon'].type == 'ordn' :
            for stavka in group['coupon'].bets :
                if stavka.bk_links != {} :
                    continue
                for key in BOOKMAKER_OFFSET.keys() :
                    # скорее всего нужна спецефичная настройка для каждой бк(предложение - создать функцию в файле бк)
                    if BOOKMAKER_OFFSET[key].HAS_API :
                        pass
                    elif BOOKMAKER_OFFSET[key].TAKES_MATCHES_LIVE :
                        # из словаря получается объект ставки
                        # должна вызываться функция find_bet
                        # подразумеваем, что в этой функции в экземпляр класса Stakva() устанавливается ссылка на матч
                        # очень возможно, что лучше перенести создание браузера в find_bet
                        pass
                    else :
                        stavka.set_bk_link(key, BOOKMAKER_OFFSET[key].get_info(stavka))
        else :
            # не умеет работать с системой ставок(когда одновременно), а может это и не нужно???
            pass
    return (key_g, DATA[key_g])

def main(DATA: dict) :

    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(find_all_links, DATA), GROUP_OFFSET.keys()))

    return DATA


