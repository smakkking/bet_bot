# здесь тестируем все модули по группам и букмекеркам

import steam.webauth as wa
from bs4 import BeautifulSoup as bs
from pprint import pprint
from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver, Stavka

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
    import grequests

    urls = [
        (grequests.Session(), 'https://betscsgo.in', 'https://betscsgo.in/login/')
    ] * 50


    for u in urls:
        u[0].cookies.set('cf_clearance', BETSCSGO_betting.CURRENT_CF_CLEARANCE)
        u[0].headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
    })


    # TASK1
    duration = time.time()
    rs = (grequests.get(u[1], session=u[0]) for u in urls)

    errors_counter = 0
    for responce in grequests.map(rs):
        try:
            if responce.status_code != 200:
                print("error")
        except:
            errors_counter += 1
    print(f"ended in {time.time() - duration} sec")
    print(f"{errors_counter} requests ended with error\n")

    # TASK2
    duration = time.time()
    rs = (grequests.get(u[1], session=u[0]) for u in urls)

    errors_counter = 0
    for responce in grequests.map(rs):
        try:
            if responce.status_code != 200:
                print("error")
        except:
            errors_counter += 1
    print(f"ended in {time.time() - duration} sec")
    print(f"{errors_counter} requests ended with error\n")


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
    'https://sun9-20.userapi.com/impf/O_fBuxflvvuDAQ4hWiKkClU5kevKL2TUgChlwg/7Xg3HApXyTQ.jpg?size=557x480&quality=96&proxy=1&sign=1e2691b1dc2b48878c7a4daf9d7c8289&c_uniq_tag=DhzWafUB25cMqfx5L4Dy0p8CqPoppvFNGF7jBg8-S_M&type=album'