from moduls.bet_manage import BOOKMAKER_OFFSET, Coupon, create_webdriver
from manage import ALL_POSTS_JSON_PATH

import json

def main(clients_DATA : dict) :
    # где и как закрывать браузеры??????????
    # нужно ввести многопроцессорность

    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        DATA = json.load(last_posts_json)
    # здесь :
    for key_g in DATA.keys() :
        for stavka in DATA[key_g]['coupon'] :
            if stavka['parse_bet'] :
                for key in BOOKMAKER_OFFSET.keys() :
                    BOOKMAKER_OFFSET[key].init_config()
                    stavka[key] = BOOKMAKER_OFFSET[key].find_bet()
    # здесь :
    for client in clients_DATA :
        for group in client['groups'] :
            if DATA[group]['parse_bet'] :
                browser = BOOKMAKER_OFFSET[client['bkm']].init_config(client)
                for stavka in DATA[group]['coupon']['bets'] :
                    BOOKMAKER_OFFSET[client['bkm']].make_bet(browser, stavka, stavka[client['bkm']], client['summ'])

    
    