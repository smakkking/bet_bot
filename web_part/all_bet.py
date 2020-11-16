from moduls.bet_manage import BOOKMAKER_OFFSET, Coupon, create_webdriver
from manage import ALL_POSTS_JSON_PATH

import json

def main(betting_array) :
    # в кач входных данных - результат работы scan_database.main()
    # делаем допущение - в купоне все элементы находятся в разных матчах и работаем с ординаром

    # сейчас работает неправильно
    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        data = json.load(last_posts_json)
    for peruser_data in betting_array :
        browser = create_webdriver(peruser_data['chrome_id'])
        for group in peruser_data['groups'] :
            cup = Coupon(data[group]['coupon'])
            for s_bet in cup.bets :
                match_url = BOOKMAKER_OFFSET[peruser_data['bkm']].find_bet(browser, s_bet)
                BOOKMAKER_OFFSET[peruser_data['bkm']].make_bet(browser, s_bet, match_url)
    