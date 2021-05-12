# здесь тестируем все модули по группам и букмекеркам

import steam.webauth as wa
from bs4 import BeautifulSoup as bs
from pprint import pprint
from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver, Stavka

from global_constants import SERVER_DATA_PATH, ALL_POSTS_JSON_PATH

import nltk, json, time
from moduls.group_moduls import BetOn_group
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


def proxy_get():
    from requests import Session
    sess = Session()

    head = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}
    sess.headers.update(head)

    sess.cookies.set('cf_clearance', 'fd7cee1d455ba16f054e95fcb9f5265370f5d36a-1612885796-0-150')

    req = sess.get('https://betscsgo.in/match/270528/')

    pos = req.text.find('matches        =')
    text = req.text[pos + len('matches        ='):]

    pos = text.find(';')
    text = text[: pos]

    t = json.loads(text)

    pprint(t)

    sess.close()


if __name__ == "__main__" :

    print(get_stavka(" https://sun9-24.userapi.com/impg/WHKwI7NcYC2d_Zp7GAhgQnDNAqTKl7w9P6uuhA/P9xe2fvRXPQ.jpg?size=1411x132&quality=96&sign=42d5c2174cb1e7ec7e5123c0c34d99ea&c_uniq_tag=QUF-rEJDND2zPCT4Md_flrHSGNjjeHFaJQ3SiTr6oa0&type=album", BetOn_group, debug=True))

    """
{
                    "bk_links": {
                        "betscsgo": {
                            "team1": "FAZE",
                            "team2": "LIQUID",
                            "bet_id": "272258",
                            "link": "https://betscsgo.in/match/272258/"
                        }
                    },
                    "summ_multiplier": 1,
                    "sum": 7500.0,
                    "match_title": "FAZE vs LIQUID",
                    "winner": "LIQUID",
                    "outcome_index": "game_winner",
                    "dogon": false,
                    "id": 1255212551
                }
    """
    'https://sun9-20.userapi.com/impf/O_fBuxflvvuDAQ4hWiKkClU5kevKL2TUgChlwg/7Xg3HApXyTQ.jpg?size=557x480&quality=96&proxy=1&sign=1e2691b1dc2b48878c7a4daf9d7c8289&c_uniq_tag=DhzWafUB25cMqfx5L4Dy0p8CqPoppvFNGF7jBg8-S_M&type=album'