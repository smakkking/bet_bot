import json
import functools
import time
from multiprocessing import Pool

from bet_manage import Stavka
from global_constants import ALL_POSTS_JSON_PATH, SERVER_DATA_PATH
from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET


def find_all_links(DATA, key_g) :
    group = DATA[key_g]
    if group['parse_bet'] :
        if group['coupon']['type'] == 'ordn' :
            for stavka in group['coupon']['bets'] :
                for key in BOOKMAKER_OFFSET.keys() :
                    if BOOKMAKER_OFFSET[key].HAS_API :
                        pass
                    elif BOOKMAKER_OFFSET[key].TAKES_MATCHES_LIVE :
                        browser = BOOKMAKER_OFFSET[key].init_config()
                        stavka[key] = BOOKMAKER_OFFSET[key].find_bet(browser, Stavka(bets=stavka))
                        browser.close()
                        browser.quit()
                    else :
                        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '.json', 'r', encoding="utf-8") as f :
                            dat = json.load(f)
                        for x in dat :
                            # совпадает ли название матча
                            if stavka['match_title'].find(x['team1']) >= 0 and stavka['match_title'].find(x['team2']) >= 0 :
                                stavka[key] = x['link']
        else :
            # не умеет работать с системой ставок(когда одновременно)
            pass
    return (key_g, DATA[key_g])


def bbet_all(DATA, client) :
    for group in client['groups'] :
        if DATA[group]['parse_bet'] :
            if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
                pass
            else :
                browser = BOOKMAKER_OFFSET[client['bookmaker']].init_config(client['chrome_dir_path'])
                for stavka in DATA[group]['coupon']['bets'] :
                    # вопрос - нужно ли здесь инициализировать экземпляр класса Stavka?
                    # и дальше работать с ним, а не со словарем
                    BOOKMAKER_OFFSET[client['bookmaker']].make_bet(browser, Stavka(bets=stavka, summ=client['bet_summ']), stavka[client['bookmaker']])
                browser.close()
                browser.quit()


def main(clients_DATA : dict, debug=False) :

    if debug :
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
    with Pool(processes=len(clients_DATA)) as pool : 
        pool.map(functools.partial(bbet_all, DATA), clients_DATA)   

    if debug :
        print('{0:.2f} spent on bet process'.format(time.time() - now))

    
    