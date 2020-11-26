from moduls.bet_manage import BOOKMAKER_OFFSET, Coupon, create_webdriver
from manage import ALL_POSTS_JSON_PATH

# еще не тестировано

import json
from multiprocessing import Pool

def find_all_links(key_g) :
    for stavka in DATA[key_g]['coupon'] :
        if stavka['parse_bet'] :
            for key in BOOKMAKER_OFFSET.keys() :
                if BOOKMAKER_OFFSET[key].HAS_API :
                    pass
                else :
                    browser = BOOKMAKER_OFFSET[key].init_config()
                    stavka[key] = BOOKMAKER_OFFSET[key].find_bet(browser, stavka)
                    browser.close()
                    browser.quit()

def bbet_all(client) :
    for group in client['groups'] :
        if DATA[group]['parse_bet'] :
            if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
                pass
            else :
                browser = BOOKMAKER_OFFSET[client['bookmaker']].init_config(client['chrome_dir_path'])
                for stavka in DATA[group]['coupon']['bets'] :
                    BOOKMAKER_OFFSET[client['bookmaker']].make_bet(browser, stavka, stavka[client['bookmaker']], client['bet_summ'])
                browser.close()
                browser.quit()

DATA = {}

def main(clients_DATA : dict) :
    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        DATA = json.load(last_posts_json)
    
    # здесь :
    with Pool(processes=len(DATA.keys())) as pool :
        pool.map(find_all_links, DATA.keys())
    
    # for key_g in DATA.keys() :
    #    for stavka in DATA[key_g]['coupon'] :
    #        if stavka['parse_bet'] :
    #            for key in BOOKMAKER_OFFSET.keys() :
    #                BOOKMAKER_OFFSET[key].init_config()
    #                stavka[key] = BOOKMAKER_OFFSET[key].find_bet()


    # здесь :
    with Pool(processes=len(clients_DATA)) as pool : 
        pool.map(bbet_all, clients_DATA)   
    #for client in clients_DATA :
    #    for group in client['groups'] :
    #        if DATA[group]['parse_bet'] :
    #            browser = BOOKMAKER_OFFSET[client['bookmaker']].init_config(client)
    #            for stavka in DATA[group]['coupon']['bets'] :
    #                BOOKMAKER_OFFSET[client['bookmaker']].make_bet(browser, stavka, stavka[client['bookmaker']], client['bet_summ'])

    
    