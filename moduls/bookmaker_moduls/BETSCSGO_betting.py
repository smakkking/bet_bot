import re
import json
from datetime import datetime, timedelta
import functools
from multiprocessing import Pool
from dateutil import parser
import steam.webauth as wa
from bs4 import BeautifulSoup as bs
from selenium.common.exceptions import WebDriverException
import logging
from selenium.common.exceptions import StaleElementReferenceException as parasha_exception
from requests import Session

import bet_manage
from global_constants import SERVER_DATA_PATH


# управляющие константы, для других модулей
NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'
WALL_URL_add = 'https://betsdota2.fun'
HAS_API = False
TAKES_MATCHES_LIVE = False


# corrected params
LIVE_MATCHES_UPDATE_TIMEm = 5

CURRENT_CF_CLEARANCE        = 'fd7cee1d455ba16f054e95fcb9f5265370f5d36a-1612885796-0-150'
CURRENT_CF_CLEARANCE_add    = '08b24ecbfedb22964cd9a8e537ec93f8dbef4057-1612885909-0-150'

# когда записываешь данные ничего к этим строкам не добавлять
OFFSET_TABLE = {
    'Победа на карте' : 'map_winner',

    'Победа в матче' : 'game_winner',

    'выиграет одну карту' : 'one_map_win',
    'выиграют одну карту' : 'one_map_win',

    'Количество карт 2.5' : 'games_count_2.5'
}

# templates parsing

def find_vs(words : list, idx : int) :
    right_team = ''
    left_team = ''

    ndx = idx - 1
    while (re.search('[A-Za-z0-9().\']+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0) :
        if (left_team.upper().find(words[ndx].upper()) < 0) :
            left_team = words[ndx] + ' ' + left_team
            ndx -= 1
        else :
            break

    left_team = bet_manage.reform_team_name(left_team)

    ndx = idx + 1
    while (re.search('[A-Za-z0-9().\']+', words[ndx]) and words[ndx].find(':') < 0) :
        if left_team.find(words[ndx].upper()) >= 0:
            break
        if (right_team.upper().find(words[ndx].upper()) < 0) :
            right_team = right_team + ' ' + words[ndx]
            ndx += 1
        else :
            break

    right_team = bet_manage.reform_team_name(right_team)

    return left_team + ' vs ' + right_team


def template1(text: str) :
    temp = [
        r'ПОБЕДА\s*НА\s*КАРТЕ',
        r'СУММА\s*СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse1(photo_url: str, words: list) :
    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 : ]
    res.outcome_index = (OFFSET_TABLE['Победа на карте'], int(words[words.index('#') + 1]))

    # res.sum = float(words[words.index('Сумма') + 3])

    return res


def template2(text: str) :
    temp = [
        # добавить \s*
        r'ПОБЕДА\s*В\s*МАТЧЕ',
        r'СУММА\s*СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse2(photo_url: str, words: list) :

    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 :]
    res.outcome_index = OFFSET_TABLE['Победа в матче']

    #res.sum = float(words[words.index('Сумма') + 3])

    return res


def template5(text : str):
    temp = [
        ['ВЫИГРАЮТ', 'ВЫИГРАЕТ'],
        'ОДНУ',
        'КАРТУ',
        'СУММА',
        'СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        if type(x) is list:
            t = False
            for z in x:
                t = t or text.find(z) >= 0
            flag = flag and t
        else:
            flag = flag and text.find(x) >= 0

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse5(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    #res.sum = float(words[words.index('Сумма') + 3])

    try:
        ndx = words.index('ВЫИГРАЮТ') - 1
    except ValueError:
        ndx = words.index('ВЫИГРАЕТ') - 1
    winner = ''
    while (re.search('[A-Za-z0-9().\']+', words[ndx]) and
            ndx >= 0 and
            words[ndx].find(':') < 0 and
            res.match_title.find(words[ndx].upper() + winner) >= 0
    ):
        winner = words[ndx].upper() + winner
        ndx -= 1

    res.outcome_index = (OFFSET_TABLE['выиграет одну карту'], winner)

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = 'YES'
    elif (side == 'right') :
        res.winner = 'NO'

    return res


def template6(text : str):
    temp = [
        'КОЛИЧЕСТВО',
        'КАРТ',
        '2.5',
        'СУММА',
        'СТАВКИ'
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        if type(x) is list:
            t = False
            for z in x:
                t = t or text.find(z) >= 0
            flag = flag and t
        else:
            flag = flag and text.find(x) >= 0

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse6(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    #res.sum = float(words[words.index('Сумма') + 3])

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = 'YES'
    elif (side == 'right') :
        res.winner = 'NO'

    res.outcome_index = OFFSET_TABLE['Количество карт 2.5']

    return res

#----------------------------------------------------------

def template3(text: str) :
    temp = [
        #r'РЕЗУЛЬТАТ\s*ОЖИДАЕТСЯ',
        r'ПОБЕДА',
    ]
    not_temp = [
        'СУММА',
        'НА',
        '+', '-'
    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse3(photo_url: str, words: list) :
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    i = 0
    while words[words.index('Победа') + 2 + i][-1] != 'P' :
        res.winner += words[words.index('Победа') + 2 + i]
        i += 1
    res.winner = bet_manage.reform_team_name(res.winner)
    try :
        res.sum = float(words[words.index('Победа') + 2 + i][ : -1])
    except ValueError:
        res.sum = float(words[words.index('Победа') + 1 + i])

    res.outcome_index = OFFSET_TABLE['Победа в матче']

    return res


def template4(text : str) :
    temp = [
        #r'РЕЗУЛЬТАТ\s*ОЖИДАЕТСЯ',
        r'ПОБЕДА\s*НА\s*КАРТЕ',
    ]
    not_temp = [
        'СУММА',
        '+', '-'
    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse4(photo_url: str, words: list) :
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    i = 0
    while words[words.index('карте') + 4 + i][-1] != 'P' :
        res.winner += words[words.index('карте') + 4 + i]
        i += 1

    res.winner = bet_manage.reform_team_name(res.winner)
    try :
        res.sum = float(words[words.index('карте') + 4 + i][ : -1])
    except ValueError :
        res.sum = float(words[words.index('карте') + 3 + i])

    res.outcome_index = (OFFSET_TABLE['Победа на карте'], int(words[words.index('карте') + 2]))

    return res


PHOTO_PARSING_TEMPLATES = [
    (template1, parse1),
    (template2, parse2),
    (template3, parse3),
    (template4, parse4),
    (template5, parse5),
    (template6, parse6),
]


# necessary functions

def find_bet() :
    with Pool(processes=2) as pool:
        new_d = pool.map(
            find_matches,
            [(WALL_URL, CURRENT_CF_CLEARANCE), (WALL_URL_add, CURRENT_CF_CLEARANCE_add)]
        )
    return new_d[0] + new_d[1]


def create_session(client_login=None, client_passwd=None) :
    user = wa.WebAuth(client_login)
    session = user.cli_login(client_passwd)

    head = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'
    }
    session.headers.update(head)
    session.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE)

    r = session.get(WALL_URL + '/login/')

    soup = bs(r.text, 'html.parser')
    form_obj = soup.find(id='openidForm')

    r = session.post('https://steamcommunity.com/openid/login', files={
        'action': (None, form_obj.find('input', {'id': 'actionInput'})['value']),
        'openid.mode': (None, form_obj.find('input', {'name': 'openid.mode'})['value']),
        'openidparams': (None, form_obj.find('input', {'name': 'openidparams'})['value']),
        'nonce': (None, form_obj.find('input', {'name': 'nonce'})['value'])
    })

    GetSesToken_betscsgo = ''
    soup = bs(r.text, 'lxml')
    scr = soup.find_all('script')
    for script in scr:
        s = str(script)
        pos = s.find('GetSessionToken')
        if pos >= 0:
            new_s = s[pos:]
            GetSesToken_betscsgo = new_s[new_s.find('\"') + 1: new_s.find(';') - 1]

    session.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE_add)
    r = session.get(WALL_URL_add + '/login/')

    GetSesToken_betsdota2 = ''
    soup = bs(r.text, 'lxml')
    scr = soup.find_all('script')
    for script in scr:
        s = str(script)
        pos = s.find('GetSessionToken')
        if pos >= 0:
            new_s = s[pos:]
            GetSesToken_betsdota2 = new_s[new_s.find('\"') + 1: new_s.find(';') - 1]

    return {
        'session' : session,
        'betscsgo_token' : GetSesToken_betscsgo,
        'betsdota2_token' : GetSesToken_betsdota2
    }


def make_bet(stavka, summ, session) :
    domen = stavka.bk_links[NAME]['link'][ :stavka.bk_links[NAME]['link'].find('match') - 1]

    if domen == WALL_URL:
        session['session'].cookies.set('cf_clearance', CURRENT_CF_CLEARANCE)
    elif domen == WALL_URL_add :
        session['session'].cookies.set('cf_clearance', CURRENT_CF_CLEARANCE_add)

    base_str = domen + '/index/placebet/'

    # здесь формируем запрос
    base_str += stavka.bk_links[NAME]['bet_id'] + '/'

    # не раб с больше\меньше и выигрыванием одной карты
    if stavka.winner == 'YES':
        base_str += '1/'
    elif stavka.winner == 'NO':
        base_str += '2/'
    else:
        if stavka.winner.find(stavka.bk_links[NAME]['team1']) >= 0 :
            base_str += '1/'
        elif stavka.winner.find(stavka.bk_links[NAME]['team2']) >= 0 :
            base_str += '2/'

    base_str += str(summ * stavka.summ_multiplier) + '/'

    if domen == WALL_URL :
        session['session'].cookies.set('cf_clearance', CURRENT_CF_CLEARANCE)
        r = session['session'].get(base_str + session['betscsgo_token'])
    else :
        session['session'].cookies.set('cf_clearance', CURRENT_CF_CLEARANCE_add)
        r = session['session'].get(base_str + session['betsdota2_token'])

    # в данной ситуации если в результате была получена страница с НОВЫМ GetSessionToken
    # (значит старый GetSessionToken больше не работает) значит ищем новый, перезаписываем
    # по времени получается достаточно недолго

    GetSesToken = None
    soup = bs(r.text, 'lxml')
    scr = soup.find_all('script')
    for script in scr:
        s = str(script)
        pos = s.find('GetSessionToken')
        if pos >= 0:
            new_s = s[pos:]
            GetSesToken = new_s[new_s.find('\"') + 1: new_s.find(';') - 1]

    if GetSesToken:
        logging.getLogger("all_bet").info("the token has changed")
        r = session['session'].get(base_str + GetSesToken)
        if domen == WALL_URL :
            session['betscsgo_token'] = GetSesToken
        else :
            session['betsdota2_token'] = GetSesToken
    else:
        logging.getLogger("all_bet").info("bet without changing token")

    return r.text


def dogon_check(stavka) :
    sess = Session()
    head = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}
    sess.headers.update(head)

    if stavka.bk_links[NAME]['link'].find(WALL_URL) >= 0:
        sess.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE)
    elif stavka.bk_links[NAME]['link'].find(WALL_URL_add) >= 0:
        sess.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE_add)

    req = sess.get(stavka.bk_links[NAME]['link'])

    # уязвимость
    pos = req.text.find('matches        =')
    text = req.text[pos + len('matches        ='):]

    pos = text.find(';')
    text = text[: pos]

    t = json.loads(text)

    sess.close()

    for outcome in t:
        if 'm_mapindex' in outcome.keys():
            if int(outcome['m_mapindex']) == 0:
                # если матч закончился, а догон остался
                if outcome['m_status'] == '3' or outcome['m_status'] == '2':
                    return True
            if int(outcome['m_mapindex']) == stavka.outcome_index[1]:
                if outcome['m_status'] == '2' and stavka.match_title.find(stavka.winner) <= stavka.match_title.find('vs') or \
                        outcome['m_status'] == '3' and stavka.match_title.find(stavka.winner) >= stavka.match_title.find('vs'):
                    return True
                elif outcome['m_status'] == '2' and stavka.match_title.find(stavka.winner) >= stavka.match_title.find('vs') or \
                        outcome['m_status'] == '3' and stavka.match_title.find(stavka.winner) <= stavka.match_title.find('vs'):
                    return False
                elif outcome['m_status'] == '5':
                    # случай если ставка отменена
                    return True
                else:
                    return None


def get_info(stavka, dat) :
    for x in dat:
        # совпадает ли название матча
        if stavka.match_title.find(x['team1']) >= 0 and stavka.match_title.find(x['team2']) >= 0:
            try:
                if type(stavka.outcome_index) is tuple or type(stavka.outcome_index) is list:
                    if stavka.outcome_index[0] == OFFSET_TABLE['Победа на карте']:
                        bet_id = x['outcomes']['map' + str(stavka.outcome_index[1])][stavka.outcome_index[0]]
                    elif stavka.outcome_index[0] == OFFSET_TABLE['выиграет одну карту']:
                        if stavka.outcome_index[1].find(x['team1']) >= 0:
                            bet_id = x['outcomes']['one_map_win'][x['team1']]
                        elif stavka.outcome_index[1].find(x['team2']) >= 0:
                            bet_id = x['outcomes']['one_map_win'][x['team2']]
                else:
                    bet_id = x['outcomes'][stavka.outcome_index]
                return {
                    'team1': x['team1'],
                    'team2': x['team2'],
                    'bet_id': bet_id,
                    'link': x['link']
                }
            except KeyError:
                return None
    logging.getLogger("find_all_links").info("match not found")

# specific functions

def find_matches(web_dict: tuple):
    def get_match(match, sess) :
        req = sess.get(match['link'])

        pos = req.text.find('matches        =')
        text = req.text[pos + len('matches        ='):]

        pos = text.find(';')
        text = text[: pos]

        t = json.loads(text)

        match['outcomes']['map1'] = {}
        match['outcomes']['map2'] = {}
        match['outcomes']['map3'] = {}
        match['outcomes']['map4'] = {}
        match['outcomes']['map5'] = {}
        match['outcomes'][OFFSET_TABLE['выиграет одну карту']] = {}

        for outcome in t:
            if outcome['m_comment'] == '' or ('m_mapindex' in outcome.keys() and outcome['m_mapindex'] == '0'):
                # победа в матче
                match['outcomes']['game_winner'] = outcome['m_id']
            elif 'm_mapindex' in outcome.keys():
                # победа на карте
                match['outcomes']['map' + str(outcome['m_mapindex'])]['map_winner'] = outcome['m_id']
            elif outcome['m_comment'].find('одну карту') >= 0:
                # команда выиграет одну карту

                if bet_manage.reform_team_name(outcome['m_comment']).find(match['team1']) >= 0:
                    match['outcomes'][OFFSET_TABLE['выиграет одну карту']][match['team1']] = outcome['m_id']
                elif bet_manage.reform_team_name(outcome['m_comment']).find(match['team2']) >= 0:
                    match['outcomes'][OFFSET_TABLE['выиграет одну карту']][match['team2']] = outcome['m_id']
            elif outcome['m_comment'] in OFFSET_TABLE.keys():
                match['outcomes'][OFFSET_TABLE[outcome['m_comment']]] = outcome['m_id']

    xPath_matches = '//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div'
    bbb = []

    sess = Session()
    head = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}
    sess.headers.update(head)
    sess.cookies.set('cf_clearance', web_dict[1])

    try:
        browser = init_config()

        bet_manage.get_html_with_browser(browser, web_dict[0], sec=15, cookies=[('cf_clearance', web_dict[1])])

        matches = browser.find_elements_by_xpath(xPath_matches)

        if matches == []:
            raise AssertionError

        for a in matches:
            if a == matches[-1] or a.text == 'Нет активных матчей':
                continue
            try:
                begin = datetime.strptime(a.find_element_by_class_name('sys-datetime').text, '%d.%m %H:%M')
            except ValueError:
                begin = datetime.strptime(a.find_element_by_class_name('sys-datetime').text, '%H:%M')
                begin = begin.replace(day=datetime.now().day, month=datetime.now().month)
            begin = begin.replace(year=datetime.now().year)

            # здесь отсеиваются матчи, чтобы не обрабатывать их неск раз

            if begin - datetime.now() > timedelta(hours=1, minutes=30):
                continue

            event_info = {}
            left_team = a.find_element_by_class_name('bet-team_left ').find_element_by_class_name('bet-team__name')
            right_team = a.find_element_by_class_name('bet-team_right ').find_element_by_class_name('bet-team__name')

            event_info['begin_date'] = begin.isoformat()
            event_info['team1'] = bet_manage.reform_team_name(
                left_team.text.replace(left_team.find_element_by_tag_name('div').text, ''))
            event_info['team2'] = bet_manage.reform_team_name(
                right_team.text.replace(right_team.find_element_by_tag_name('div').text, ''))

            event_info['link'] = a.find_element_by_class_name('sys-matchlink').get_attribute('href')
            event_info['outcomes'] = {}
            get_match(event_info, sess)

            bbb.append(event_info)
    finally:
        browser.quit()
        sess.close()

    return bbb


def init_config() :
    driver = bet_manage.create_webdriver()
    return driver



