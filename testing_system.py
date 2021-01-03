# здесь тестируем все модули по группам и букмекеркам

from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver

from global_constants import BET_PROJECT_ROOT

import nltk, json, time
from moduls.group_moduls import ExpertMnenie_group
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

    with open(BET_PROJECT_ROOT + 'server_data/test.json', 'w') as f :
        json.dump(bbb, f, indent=4)

def get_stavka(photo_url, group) :
    YandexAPI_detection.create_new_token(debug=True)
    a = YandexAPI_detection(photo_url)
    text = a.text_detection()
    text_nltk = nltk.word_tokenize(text)
    text = text.upper()

    stavka = None

    for (tmp, parse) in group.BET_TEMPLATES :
        if tmp(text) :
            stavka = parse(photo_url, text_nltk)
    if stavka is None :
        return None
    else :
        return stavka.__json_repr__()

def cf_scraper() :
    import requests

    s = requests.Session()
    head = {
        'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }
    s.headers.update(head)
    s.cookies.set('cf_clearance', '5a89c14b8b4ee0f11c4e471a778912a5c8222ac5-1609228344-0-150')

    r = s.get('https://betscsgo.in/match/265584/')
    print(r.text)

def hdless_betscsgo() :
    driver = create_webdriver()
    get_html_with_browser(driver, BETSCSGO_betting.WALL_URL, sec=5, cookies=[('cf_clearance', BETSCSGO_betting.CURRENT_CF_CLEARANCE)])

    cook = driver.get_cookies()

    driver = create_webdriver(hdless=True)
    get_html_with_browser(driver, BETSCSGO_betting.WALL_URL, sec=5)

    for c in cook :
        driver.add_cookie(c)

    time.sleep(10)

    with open('file.html', 'w') as f :
        f.write(driver.page_source)

if __name__ == "__main__" :
    hdless_betscsgo()
    """
    {
        "match_title": "FORZESCHOOL VS STATE21",
        "winner": "FORZESCHOOL",
        "outcome_index": [
            "map_winner", 1
        ],
        "dogon": true,
        "bk_links": {
            "betscsgo": {
                "link": "https://betscsgo.in/match/265584/"
            }
        }
    }
    """
    '(python3 load_last_data.py) | (python3 all_bet.py) | (python3 check_dogon.py) | (python3 find_matches_live.py)'
    pass
