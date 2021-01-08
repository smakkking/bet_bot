# здесь тестируем все модули по группам и букмекеркам
import steampy
from pprint import pprint
from bet_manage import LastGroupPost, YandexAPI_detection, get_html_with_browser, create_webdriver

from global_constants import SERVER_DATA_PATH

import nltk, json, time
from moduls.group_moduls import CSgo99percent_group
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

def placebet(login, passwd) :

    # данная ф-ия осуществляет авторизацию на betscsgo

    import steam.webauth as wa
    from bs4 import BeautifulSoup as bs

    user = wa.WebAuth(login)
    session = user.cli_login(passwd)

    head = {
        'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }
    session.headers.update(head)
    session.cookies.set('cf_clearance', BETSCSGO_betting.CURRENT_CF_CLEARANCE)

    r = session.get('https://betscsgo.in/login/')

    soup = bs(r.text, 'html.parser')
    form_obj = soup.find(id='openidForm')

    r = session.post('https://steamcommunity.com/openid/login', files={
        'action': (None, form_obj.find('input', {'id': 'actionInput'})['value']),
        'openid.mode': (None,form_obj.find('input', {'name': 'openid.mode'})['value']),
        'openidparams': (None,form_obj.find('input', {'name': 'openidparams'})['value']),
        'nonce': (None,form_obj.find('input', {'name': 'nonce'})['value'])
    })

    # поиск GetSessionToken
    soup = bs(r.text, 'html.parser')
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
    testing_group(CSgo99percent_group, 100)
