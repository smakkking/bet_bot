# здесь тестируем все модули по группам и букмекеркам

import steam.webauth as wa
from bs4 import BeautifulSoup as bs
from pprint import pprint
from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver, read_groups

from global_constants import SERVER_DATA_PATH

import nltk, json, time
from moduls.group_moduls import Aristocrat_group
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
            stavka = parse(photo_url, text_nltk)

    return None if (stavka is None) else stavka.__json_repr__()

def placebet(login, passwd, i) :

    user = wa.WebAuth(login)
    session = user.cli_login(passwd)

    head = {
        'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }
    #session.headers.update(head)
    session.cookies.set('cf_clearance', '869adfab27a1a8e792dfedd9959f36cd45e122c1-1610387075-0-150')

    r = session.get('https://betscsgo.in/login/')

    soup = bs(r.text, 'lxml')
    form_obj = soup.find(id='openidForm')

    r = session.post('https://steamcommunity.com/openid/login', files={
        'action': (None, form_obj.find('input', {'id': 'actionInput'})['value']),
        'openid.mode': (None,form_obj.find('input', {'name': 'openid.mode'})['value']),
        'openidparams': (None,form_obj.find('input', {'name': 'openidparams'})['value']),
        'nonce': (None,form_obj.find('input', {'name': 'nonce'})['value'])
    })

    # поиск GetSessionToken
    GetSesToken = None

    soup = bs(r.text, 'lxml')
    scr = soup.find_all('script')
    for script in scr :
        s = str(script)
        pos = s.find('GetSessionToken')
        if pos >= 0 :
            new_s = s[pos : ]
            GetSesToken = new_s[new_s.find('\"') +  1 : new_s.find(';') - 1]

    # как пример ставки, не более
    session.close()

    return GetSesToken

def undetected_bets_test(group) :
    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'r') as f:
        data = json.load(f)
    reupload = []

    driver = create_webdriver()

    for link in data[group.NAME] :
        bet = get_stavka(link, group)
        get_html_with_browser(driver, link)
        if bet :
            pprint(bet)
        else :
            reupload.append(link)
        input()
    driver.close()
    data[group.NAME] = reupload

    with open(SERVER_DATA_PATH + 'undetected_bets.json', 'w') as f :
        json.dump(data, f, indent=4)


def cf_scrapper() :
    from requests_html import HTMLSession

    session = HTMLSession()
    #session.proxies = {'http':  'socks5://ps3540:A_u0GQ1ODBTwRAKFRfSv@138.124.180.99:8000', 'https': f'socks5://ps3540:A_u0GQ1ODBTwRAKFRfSv@138.124.180.99:8000'}
    session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}

    hosts = [
        '172.67.22.114',
        '104.22.29.216',
        '104.22.28.216',
        '172.67.167.202',
        '104.24.117.219',
        '104.24.116.219',
        '172.67.27.87',
        '104.22.79.103',
        '104.22.78.103'
    ]
    for ip in hosts :
        try :
            request = session.get('https://' + ip + '/', headers={'host' : 'betscsgo.in'})
            print('connected successfully')
        except :
            continue

    session.close()

    request.html.render()  # драйвер для JS

    print(request.html.html)  # Получаем контент)

def cf_scrapper2() :
    import cloudscraper

    scraper = cloudscraper.create_scraper()
    print(scraper.get("https://betscsgo.in").text)

if __name__ == "__main__" :

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