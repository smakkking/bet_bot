# здесь тестируем все модули по группам и букмекеркам

import steam.webauth as wa
from bs4 import BeautifulSoup as bs
from pprint import pprint
from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver, read_groups

from global_constants import SERVER_DATA_PATH, ALL_POSTS_JSON_PATH

import nltk, json, time
from moduls.group_moduls import Aristocrat_group, SaveMoney_group
from moduls.bookmaker_moduls import BETSCSGO_betting

def testing_group(group, N) :
    p = LastGroupPost(group.WALL_URL)
    YandexAPI_detection.create_new_token(debug=True)
    
    if N // 100 == 0 :
        p.get(0, N)
    else :
        for offset in range(N // 100) :
            p.get(100 * offset, 100)
        if N % 100 != 0 :
            p.get((N // 100) * 100, N % 100)
         

    bbb = []

    for photo in p.photo_list :
        #print(photo)
        try :
            a = YandexAPI_detection(photo)
            text = a.text_detection()
            text_nltk = nltk.word_tokenize(text)
            text = text.upper()

            stavka = None

            for (tmp, parse) in group.BET_TEMPLATES :
                if tmp(text) :
                    stavka = parse(photo, text_nltk)
        except Exception as e :
            bbb.append({
                'link' : photo,
                'text' : '',
                'stavka' : f'failed because of: {e}'
            })
        else :
            if stavka is None :
                bbb.append({
                    'link' : photo,
                    'text' : text,
                    'stavka' : 'not_bet'
                })
            else :
                bbb.append({
                    'link' : photo,
                    'text' : text,
                    'stavka' : stavka.__json_repr__(),
                })

    driver = create_webdriver()
    undetected_bets = []

    for tape in bbb :
        get_html_with_browser(driver, tape['link'])
        pprint(tape['stavka'])
        symb = input()
        if symb == 'w' :
            undetected_bets.append(tape['link'])

    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'r') as f :
        data = json.load(f)

    if group.NAME in data :
        data[group.NAME].extend(undetected_bets)
    else :
        data[group.NAME] = undetected_bets

    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'w') as f :
        json.dump(data, f, indent=4)

    driver.close()

def get_stavka(photo_url, group, debug=False) :
    YandexAPI_detection.create_new_token()
    a = YandexAPI_detection(photo_url)
    text = a.text_detection()

    text_nltk = nltk.word_tokenize(text)

    if debug :
        print(text)
        print(text_nltk)

    text = text.upper()
    stavka = None

    for (tmp, parse) in group.BET_TEMPLATES :
        if tmp(text) :
            print('iam')
            stavka = parse(photo_url, text_nltk)

    return None if (stavka is None) else stavka.__json_repr__()

def undetected_bets_test(group) :
    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'r') as f:
        data = json.load(f)
    reupload = []

    driver = create_webdriver()

    for link in data[group.NAME] :
        get_html_with_browser(driver, link)
        bet = get_stavka(link, group, debug=True)
        pprint(bet)
        s = input()
        if s == 'w' :
            reupload.append(link)
    driver.close()
    data[group.NAME] = reupload

    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'w') as f :
        json.dump(data, f, indent=4)


def f1() :
    with open(ALL_POSTS_JSON_PATH, 'r') as f:
        json.load(f)

def f2() :
    x = {}
    with open(ALL_POSTS_JSON_PATH, 'r') as f:
        json.dump(x, f)

if __name__ == "__main__" :

    from multiprocessing import Process

    p1 = Process(target=f1)
    p2 = Process(target=f2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    """
{
        "bk_links": {
            "betscsgo": {
                "team1": "SPROUT",
                "team2": "TBD",
                "bet_id": "267019",
                "link": "https://betscsgo.in/match/267019/"
            }
        },
        "summ_multiplier": 1,
        "sum": 7500.0,
        "match_title": "SPROUT vs TBD",
        "winner": "SPROUT",
        "outcome_index": "game_winner",
        "dogon": false
    }
    """

    '(python3 find_matches_live.py) | (python3 load_last_data.py) | (python3 all_bet.py) | (python3 check_dogon.py) '
    'https://sun9-20.userapi.com/impf/O_fBuxflvvuDAQ4hWiKkClU5kevKL2TUgChlwg/7Xg3HApXyTQ.jpg?size=557x480&quality=96&proxy=1&sign=1e2691b1dc2b48878c7a4daf9d7c8289&c_uniq_tag=DhzWafUB25cMqfx5L4Dy0p8CqPoppvFNGF7jBg8-S_M&type=album'