import json
import functools
import time
from multiprocessing import Pool

from bet_manage import Stavka
from global_constants import ALL_POSTS_JSON_PATH, SERVER_DATA_PATH
from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET


def find_all_links(DATA, key_g) :
    # TODO превращает все словари в объекты ставок
    group = DATA[key_g]
    if group['parse_bet'] :
        if group['coupon']['type'] == 'ordn' :
            new_list = []
            for stavka in group['coupon']['bets'] :
                for key in BOOKMAKER_OFFSET.keys() :
                    new_bet = Stavka(bets=stavka)
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
                            if new_bet.match_title.find(x['team1']) >= 0 and new_bet.match_title.find(x['team2']) >= 0 :
                                new_bet.set_bk_link(key, x['link'])
                new_list.append(new_bet)
            group['coupon']['bets'] = new_list
        else :
            # не умеет работать с системой ставок(когда одновременно)
            pass
    return (key_g, DATA[key_g])


def bbet_all(DATA, client) :
    # уже подразумеваем, что в словарях лежат объекты ставок
    for group in client['groups'] :
        if DATA[group]['parse_bet'] :
            if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
                pass
            else :
                browser = BOOKMAKER_OFFSET[client['bookmaker']].init_config(client['chrome_dir_path'])
                for stavka in DATA[group]['coupon']['bets'] :
                    BOOKMAKER_OFFSET[client['bookmaker']].make_bet(browser, stavka, summ=client['bet_summ'])
                browser.close()
                browser.quit()


def main(clients_DATA : dict, main_logger=None) :

    if main_logger :
        now = time.time()

    DATA = {}
    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        DATA = json.load(last_posts_json)

    # здесь :
    # в DATA записываются ссылки на матчи в разных бк для каждой ставки
    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(find_all_links, DATA), GROUP_OFFSET.keys()))

    # здесь :
    # для каждого клиента происходит процесс ставки
    if clients_DATA != [] :
        with Pool(processes=len(clients_DATA)) as pool :
            pool.map(functools.partial(bbet_all, DATA), clients_DATA)

    if main_logger :
        main_logger.info('{0:.2f} spent on bet process'.format(time.time() - now))

    
    