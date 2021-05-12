import re
import json
from datetime import datetime, timedelta
from multiprocessing import Pool, Process
from bs4 import BeautifulSoup as bs
import logging
from requests import Session
from requests import exceptions as req_except
import time
from contextlib import redirect_stderr
from pprint import pformat
import pickle
from itertools import chain
from dateutil import parser

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import steam.webauth as wa

import bet_manage
from global_constants import SERVER_DATA_PATH, MOZILLA_USER_AGENT

with open(SERVER_DATA_PATH + 'logs/grequests.txt', 'w') as f:
    with redirect_stderr(f):
        import grequests

# управляющие константы, для других модулей
NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'
WALL_URL_add = 'https://betsdota2.fun'

HAS_API = False
TAKES_MATCHES_LIVE = False
USE_PROXY = True


# corrected params
LIVE_MATCHES_UPDATE_TIMEm = 5

CURRENT_CF_CLEARANCE = 'ed996958f2e642d1b8e6345d39519fa8d12f8ac1-1615805638-0-150'
CURRENT_CF_CLEARANCE_add = '77bf042db21f3343855010f78e744e4510cc4224-1615805643-0-150'

# когда записываешь данные ничего к этим строкам не добавлять
OFFSET_TABLE = {
    'Победа на карте': 'map_winner',

    'Победа в матче': 'game_winner',

    'выиграет одну карту': 'one_map_win',
    'выиграют одну карту': 'one_map_win',

    'Количество карт 2.5': 'games_count_2.5',
    'Количество карт 4.5': 'games_count_4.5',
}

# templates parsing


def find_vs(words: list, idx: int):
    right_team = ''
    left_team = ''

    ndx = idx - 1
    while (re.search('[A-Za-z0-9().\']+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0):
        if (left_team.upper().find(words[ndx].upper()) < 0):
            left_team = words[ndx] + ' ' + left_team
            ndx -= 1
        else:
            break

    left_team = bet_manage.reform_team_name(left_team)

    ndx = idx + 1
    while (re.search('[A-Za-z0-9().\']+', words[ndx]) and words[ndx].find(':') < 0):
        if (right_team.upper().find(words[ndx].upper()) < 0):
            right_team = right_team + ' ' + words[ndx]
            ndx += 1
        else:
            break

    right_team = bet_manage.reform_team_name(right_team)

    return left_team + ' vs ' + right_team


def template1(text: str):
    temp = [
        r'ПОБЕДА\s*НА\s*КАРТЕ',
        r'СУММА\s*СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp:
        flag = flag and re.search(x, text)

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse1(photo_url: str, words: list):
    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left'):
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right'):
        res.winner = res.match_title[res.match_title.find('vs') + 3:]
    res.outcome_index = (OFFSET_TABLE['Победа на карте'], int(
        words[words.index('#') + 1]))

    try:
        res.sum = float(words[words.index('Сумма') + 3])
    except:
        pass

    return res


def template2(text: str):
    temp = [
        # добавить \s*
        r'ПОБЕДА\s*В\s*МАТЧЕ',
        r'СУММА\s*СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp:
        flag = flag and re.search(x, text)

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse2(photo_url: str, words: list):

    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left'):
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right'):
        res.winner = res.match_title[res.match_title.find('vs') + 3:]
    res.outcome_index = OFFSET_TABLE['Победа в матче']

    try:
        res.sum = float(words[words.index('Сумма') + 3])
    except:
        pass

    return res


def template5(text: str):
    temp = [
        ('ВЫИГРАЮТ', 'ВЫИГРАЕТ'),
        'ОДНУ',
        'КАРТУ',
        'СУММА',
        'СТАВКИ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp:
        if type(x) is tuple:
            t = False
            for z in x:
                t = t or text.find(z) >= 0
            flag = flag and t
        else:
            flag = flag and text.find(x) >= 0

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse5(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    try:
        res.sum = float(words[words.index('Сумма') + 3])
    except:
        pass

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
    if (side == 'left'):
        res.winner = 'YES'
    elif (side == 'right'):
        res.winner = 'NO'

    return res


def template6(text: str):
    temp = [
        'КОЛИЧЕСТВО',
        'КАРТ',
        ('2.5', '4.5'),
        'СУММА',
        'СТАВКИ'
    ]
    not_temp = [

    ]

    flag = True
    for x in temp:
        if type(x) is tuple:
            t = False
            for z in x:
                t = t or text.find(z) >= 0
            flag = flag and t
        else:
            flag = flag and text.find(x) >= 0

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse6(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))
    try:
        res.sum = float(words[words.index('Сумма') + 3])
    except:
        pass

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left'):
        res.winner = 'YES'
    elif (side == 'right'):
        res.winner = 'NO'

    if '2.5' in words:
        res.outcome_index = OFFSET_TABLE['Количество карт 2.5']
    elif '4.5' in words:
        res.outcome_index = OFFSET_TABLE['Количество карт 4.5']

    return res

# ----------------------------------------------------------


def template3(text: str):
    temp = [
        # r'РЕЗУЛЬТАТ\s*ОЖИДАЕТСЯ',
        r'ПОБЕДА',
    ]
    not_temp = [
        'СУММА',
        'НА',
    ]

    flag = True
    for x in temp:
        flag = flag and re.search(x, text)

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse3(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    i = 0
    while words[words.index('Победа') + 2 + i][-1] != 'P':
        res.winner += words[words.index('Победа') + 2 + i]
        i += 1
    res.winner = bet_manage.reform_team_name(res.winner)
    try:
        res.sum = float(words[words.index('Победа') + 2 + i][: -1])
    except ValueError:
        res.sum = float(words[words.index('Победа') + 1 + i])

    res.outcome_index = OFFSET_TABLE['Победа в матче']

    return res


def template4(text: str):
    temp = [
        # r'РЕЗУЛЬТАТ\s*ОЖИДАЕТСЯ',
        r'ПОБЕДА\s*НА\s*КАРТЕ',
    ]
    not_temp = [
        'СУММА',
    ]

    flag = True
    for x in temp:
        flag = flag and re.search(x, text)

    for x in not_temp:
        flag = flag and text.find(x) < 0
    return flag


def parse4(photo_url: str, words: list):
    res = bet_manage.Stavka()

    res.match_title = find_vs(words, words.index('vs'))

    i = 0
    while words[words.index('карте') + 4 + i][-1] != 'P':
        res.winner += words[words.index('карте') + 4 + i]
        i += 1

    res.winner = bet_manage.reform_team_name(res.winner)
    try:
        res.sum = float(words[words.index('карте') + 4 + i][: -1])
    except ValueError:
        res.sum = float(words[words.index('карте') + 3 + i])

    res.outcome_index = (OFFSET_TABLE['Победа на карте'], int(
        words[words.index('карте') + 2]))

    return res


PHOTO_PARSING_TEMPLATES = [
    (template1, parse1),
    (template2, parse2),
    (template3, parse3),
    (template4, parse4),
    (template5, parse5),
    (template6, parse6),
]

# find_mathces_live interface
def find_bet(last_data):

    betscsgo = []
    betsdota2 = []

    for data in last_data:
        if data['link'].find(WALL_URL) >= 0:
            betscsgo.append(data['link'])
        elif data['link'].find(WALL_URL_add) >= 0:
            betsdota2.append(data['link'])

    duration = time.time()
    try:
        with Pool(processes=2) as pool:
            new_d = pool.map(
                find_matches,
                [(WALL_URL, CURRENT_CF_CLEARANCE, betscsgo),
                (WALL_URL_add, CURRENT_CF_CLEARANCE_add, betsdota2)]
            )
    except AssertionError:
        logging.getLogger("find_matches_live").error(NAME + " failed")
        return last_data

    logging.getLogger("find_matches_live").info(NAME + " ended in {}".format(time.time() - duration))
    new_d = dict(list(new_d[0].items()) + list(new_d[1].items()))

    new_data = []
    for data in last_data:
        if data['link'] in new_d.keys():
            if new_d[data['link']]['outcomes']:
                new_data.append(new_d[data['link']])
            else:
                new_data.append(data)
            new_d.pop(data['link'])

    new_data.extend(new_d.values())

    return new_data


def find_matches(web_dict: tuple):
    def get_match(match, sess):
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
                match['outcomes']['map' +
                                  str(outcome['m_mapindex'])]['map_winner'] = outcome['m_id']
            elif outcome['m_comment'].find('одну карту') >= 0:
                # команда выиграет одну карту

                if bet_manage.reform_team_name(outcome['m_comment']).find(match['team1']) >= 0:
                    match['outcomes'][OFFSET_TABLE['выиграет одну карту']
                                      ][match['team1']] = outcome['m_id']
                elif bet_manage.reform_team_name(outcome['m_comment']).find(match['team2']) >= 0:
                    match['outcomes'][OFFSET_TABLE['выиграет одну карту']
                                      ][match['team2']] = outcome['m_id']
            elif outcome['m_comment'] in OFFSET_TABLE.keys():
                match['outcomes'][OFFSET_TABLE[outcome['m_comment']]
                                  ] = outcome['m_id']

    xPath_matches = '//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div'
    bbb = []

    with Session() as sess, init_config(mode='find_matches') as browser:

        head = {'User-Agent': MOZILLA_USER_AGENT}
        sess.headers.update(head)
        sess.cookies.set('cf_clearance', web_dict[1])
        # основная проблема выброса исключения StaleEelement - меняется отсчет времени до начала матча
        
        # надеюсь, что этот цикл не будет бесконечным
        bet_manage.get_html_with_browser(browser, web_dict[0], sec=7)
        while True:
            try:
                matches = browser.find_elements_by_xpath(xPath_matches)

                if matches == []:
                    raise NoSuchElementException

                for a in matches:
                    if a == matches[-1] or a.text == 'Нет активных матчей':
                        continue
                    try:
                        begin = datetime.strptime(a.find_element_by_class_name(
                            'sys-datetime').text, '%d.%m %H:%M')
                    except ValueError:
                        begin = datetime.strptime(
                            a.find_element_by_class_name('sys-datetime').text, '%H:%M')
                        begin = begin.replace(
                            day=datetime.now().day, month=datetime.now().month)
                    begin = begin.replace(year=datetime.now().year)

                    if begin - datetime.now() > timedelta(hours=3):
                        # если есть один матч, который начинаеть более чем через 3 часа, 
                        # то все остальные начинаются также более чем через 3 часа.
                        # надеюсь, что они все берутся в таком порядке, в котором представлены на сайте
                        break

                    event_info = {}

                    event_info['link'] = a.find_element_by_class_name(
                        'sys-matchlink').get_attribute('href')

                    left_team = a.find_element_by_class_name(
                        'bet-team_left ').find_element_by_class_name('bet-team__name')
                    right_team = a.find_element_by_class_name(
                        'bet-team_right ').find_element_by_class_name('bet-team__name')

                    event_info['begin_date'] = begin.isoformat()
                    event_info['team1'] = bet_manage.reform_team_name(
                        left_team.text.replace(left_team.find_element_by_tag_name('div').text, ''))
                    event_info['team2'] = bet_manage.reform_team_name(
                        right_team.text.replace(right_team.find_element_by_tag_name('div').text, ''))

                    event_info['outcomes'] = {}

                    bbb.append(event_info)
                break
            except (NoSuchElementException, StaleElementReferenceException):
                time.sleep(2)
                bbb = []

        for event_info in bbb:
            if not event_info['outcomes']:
                if event_info['link'] in web_dict[2]:
                    if parser.parse(event_info['begin_date']) > datetime.now():
                        continue
                try:
                    get_match(event_info, sess)
                except (req_except.ConnectionError, json.decoder.JSONDecodeError):
                    continue

    return dict([(b['link'], b) for b in bbb])


# relogin_clients.py interface
def relogin(data):
    # как отслеживать ошибки(например массовый нелогин)

    tmp = []
    for client in data:
        if client['bookmaker'] == NAME:
            tmp.append(bet_manage.Client(client))
    data = tmp

    session_array = {}
    with open(SERVER_DATA_PATH + NAME + '/proxy_table.json', 'r') as f:
        PROXY_TABLE = json.load(f)

    for i, client in enumerate(data):
        sess_info = create_session(
            client,
            proxy_data=PROXY_TABLE[i % len(PROXY_TABLE)]
        )
        if sess_info:
            sess_info['proxy_offset'] = i % len(PROXY_TABLE)
            session_array[client.id] = sess_info
            logging.getLogger('server_data_update').info(
                f"{client.id} login successfuly")
        else:
            logging.getLogger('server_data_update').error(
                f"can't login user{client.id}")
        time.sleep(5)

    with open(SERVER_DATA_PATH + NAME + '/sessions.json', 'w') as f:
        json.dump(session_array, f, indent=4)


def create_session(client, proxy_data=None):
    try:
        user = wa.WebAuth(client.bookmaker_login)
        session = user.login(client.bookmaker_password)
    except (wa.LoginIncorrect, wa.CaptchaRequired):
        return None

    head = {'User-Agent': MOZILLA_USER_AGENT}
    session.headers.update(head)

    for cook in proxy_data['cookies']:
        session.cookies.set(cook['name'], cook['value'], domain=cook['domain'])
    session.proxies.update(proxy_data['proxy'])

    MAX_TIME_CONNECTION_LOGIN = 5
    k = 0
    while True:
        try:
            r = session.get(WALL_URL + '/login/')

            soup = bs(r.text, 'lxml')
            form_obj = soup.find(id='openidForm')

            r = session.post('https://steamcommunity.com/openid/login', files={
                'action': (None, form_obj.find('input', {'id': 'actionInput'})['value']),
                'openid.mode': (None, form_obj.find('input', {'name': 'openid.mode'})['value']),
                'openidparams': (None, form_obj.find('input', {'name': 'openidparams'})['value']),
                'nonce': (None, form_obj.find('input', {'name': 'nonce'})['value'])
            })

            # поиск банка
            try:
                soup = bs(r.text, 'lxml')
                bank = float(soup.find('span', class_='sys-userwallet').text)
            except AttributeError:
                bank = 1000

            r = session.get(WALL_URL_add + '/login/')

            break
        except req_except.ConnectionError:
            k += 1
            if k >= MAX_TIME_CONNECTION_LOGIN:
                return None
            time.sleep(4)
            continue

    with open(SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client.id), 'wb') as f:
        pickle.dump(session, f)
        session = SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client.id)

    return {
        'session': session,
        'bank': bank
    }


# check_dogon interface
def dogon_check(stavka):
    with Session() as sess:
        sess.headers.update({'User-Agent': MOZILLA_USER_AGENT})
        sess.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE,
                         domain='betscsgo.in')
        sess.cookies.set('cf_clearance', CURRENT_CF_CLEARANCE_add,
                         domain='betsdota2.fun')
        err_k = 0
        while True:
            try:
                req = sess.get(stavka.bk_links[NAME]['link'])
                # уязвимость
                pos = req.text.find('matches        =')
                text = req.text[pos + len('matches        ='):]
                pos = text.find(';')
                text = text[: pos]
                t = json.loads(text)

                break
            except (req_except.ConnectionError, json.decoder.JSONDecodeError):
                err_k += 1
                if err_k == 3:
                    return None
                time.sleep(2)

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


# find_all_links interface
def get_info(stavka, dat):
    for x in dat:
        # в данном участке кода должны исправляться ошибки распознавания(только так, чтобы это не влияло на другие бк)
        if stavka.match_title.find(x['team1']) >= 0 or stavka.match_title.find(x['team2']) >= 0:
            try:
                if type(stavka.outcome_index) is tuple or type(stavka.outcome_index) is list:
                    if stavka.outcome_index[0] == OFFSET_TABLE['Победа на карте']:
                        bet_id = x['outcomes']['map' +
                                               str(stavka.outcome_index[1])][stavka.outcome_index[0]]
                    elif stavka.outcome_index[0] == OFFSET_TABLE['выиграет одну карту']:
                        if stavka.outcome_index[1].find(x['team1']) >= 0:
                            bet_id = x['outcomes']['one_map_win'][x['team1']]
                        elif stavka.outcome_index[1].find(x['team2']) >= 0:
                            bet_id = x['outcomes']['one_map_win'][x['team2']]
                else:
                    bet_id = x['outcomes'][stavka.outcome_index]

                # на случай ошибок распознавания
                if stavka.winner.find(x['team1']) >= 0:
                    stavka.winner = x['team1']
                elif stavka.winner.find(x['team2']) >= 0:
                    stavka.winner = x['team2']

                stavka.match_title = x['team1'] + ' vs ' + x['team2']
                return {
                    'team1': x['team1'],
                    'team2': x['team2'],
                    'bet_id': bet_id,
                    'link': x['link']
                }
            except KeyError:
                return None


# all_bet.py interface
class LocalClient(bet_manage.Client):
    def __init__(self, info: dict):
        self.queries = []  # кортежи вида (запрос, сумма)
        self.betscsgo_sessiontoken = False
        self.bestdota2_sessiontoken = False

        super().__init__(info)

        self.session = None
        self.bank = 0
        self.proxy_offset = 0

    def append_base_request(self, stavka, summ):
        """ Creates HTTPS query for Stavka object(without GetSessionToken). """

        domain = stavka.bk_links[NAME]['link'][:stavka.bk_links[NAME]['link'].find(
            'match') - 1]
        base_str = domain + '/index/placebet/' + \
            stavka.bk_links[NAME]['bet_id'] + '/'

        if stavka.winner == 'YES':
            base_str += '1/'
        elif stavka.winner == 'NO':
            base_str += '2/'
        else:
            if stavka.winner.find(stavka.bk_links[NAME]['team1']) >= 0:
                base_str += '1/'
            elif stavka.winner.find(stavka.bk_links[NAME]['team2']) >= 0:
                base_str += '2/'

        base_str += str(summ * stavka.summ_multiplier) + '/'
        self.queries.append(
            (base_str, summ)
        )

    def create_queries(self, DATA):
        """ Returns the list of HTTPS queries for one client"""

        for group in self.groups:
            if DATA[group]['parse_bet']:
                for stavka in DATA[group]['coupon'].bets:
                    if stavka.bk_links.get(self.bookmaker) is None:
                        continue
                    self.append_base_request(
                        stavka,
                        self.bet_summ if self.bet_mode == 'fixed' or stavka.sum == 0
                        else stavka.sum * self.bank / DATA[group]['bank']
                    )

    def set_session_info(self, info):
        with open(info['session'], 'rb') as f:
            self.session = pickle.load(f)
        self.bank = info['bank']
        self.proxy_offset = info['proxy_offset']

    def add_tokens(self):
        tmp = []
        for query, summ in self.queries:
            if query.find(WALL_URL) >= 0:
                query += self.betscsgo_sessiontoken
            elif query.find(WALL_URL_add) >= 0:
                query += self.bestdota2_sessiontoken

            tmp.append(
                (query, summ)
            )

        self.queries = tmp

    def parse_token(self, resp):

        GetSesToken = None

        soup = bs(resp.text, 'lxml')
        scr = soup.find_all('script')
        for script in scr:
            s = str(script)
            pos = s.find('GetSessionToken')
            if pos >= 0:
                new_s = s[pos:]
                GetSesToken = new_s[new_s.find('\"') + 1: new_s.find(';') - 1]

        if resp.url.find(WALL_URL) >= 0:
            self.betscsgo_sessiontoken = GetSesToken
        elif resp.url.find(WALL_URL_add) >= 0:
            self.bestdota2_sessiontoken = GetSesToken

    def __repr__(self):
        return str(self.__dict__)


class ProxyServer:
    def __init__(self, index, array):
        self.clients = []

        for client in array:
            if client.proxy_offset == index:
                self.clients.append(client)

    def get_clients_tokens(self):
        betscsgo_token = []
        betsdota2_token = []

        for i, client in enumerate(self.clients):
            for query, summ in client.queries:
                client.betscsgo_sessiontoken |= query.find(WALL_URL) >= 0
                client.bestdota2_sessiontoken |= query.find(WALL_URL_add) >= 0

            if client.betscsgo_sessiontoken:
                betscsgo_token.append(i)
            elif client.bestdota2_sessiontoken:
                betsdota2_token.append(i)

        if betscsgo_token:
            self.collect_tokens(WALL_URL, betscsgo_token)
        if betsdota2_token:
            self.collect_tokens(WALL_URL_add, betsdota2_token)

    def collect_tokens(self, url, token_indexes: list):
        rs1 = [grequests.get(url, session=self.clients[index].session)
               for index in token_indexes]
        resp = grequests.map(rs1, size=10)

        for i, index in enumerate(token_indexes):
            self.clients[index].parse_token(resp[i])

    def send_queries(self):
        duration = time.time()

        stats = {
            'all_queries': 0,
            'success': 0,
            'ids': [],
            'log_message': [],
            'payment': {}
        }

        for client in self.clients:
            client.add_tokens()
            responce = []
            for query, summ in client.queries:
                responce.append(client.session.get(query))

            stats['all_queries'] += len(client.queries)
            stats['ids'].append(client.id)
            stats['payment'][client.id] = 0

            for i, value in enumerate(responce):

                if value.status_code != 200:
                    continue

                try:
                    result = value.json()
                except ValueError:
                    result = {
                        'success': False,
                        'error': "decode error"
                    }

                if result['success']:
                    stats['success'] += 1
                    stats['payment'][client.id] += client.queries[i][1]
                else:
                    stats['log_message'].append({
                        'client_id': client.id,
                        'error': result['error'],
                        'url': value.url,
                        'status_code': value.status_code
                    })

            if stats['payment'][client.id] == 0:
                stats['payment'].pop(client.id)

        if stats['all_queries']:
            logging.getLogger("created_bets").info(
                f"time_passed= {time.time() - duration}\n" +
                f"\tsuccess= {stats['success']}\n" +
                f"\tall= {stats['all_queries']}\n" +
                (pformat(stats['log_message']) if stats['log_message'] else '')
            )

        return stats['payment']

    def bet(self):
        self.get_clients_tokens()
        return self.send_queries()


def mass_bet(DATA, clients, payment):
    duration = time.time()

    # clients - отобраные для бк словари для инициализации в класс LocalClient
    # выяснить какие ключи используются(либо числа, либо строки)
    # TODO обработка процессов через декораторы

    client_array = [LocalClient(v) for v in clients]
    with open(SERVER_DATA_PATH + NAME + '/sessions.json', 'r') as f:
        sessions = json.load(f)  # ключи - строки

    for client in client_array:
        client.set_session_info(sessions[str(client.id)])
        client.create_queries(DATA)

    with open(SERVER_DATA_PATH + NAME + '/proxy_table.json', 'r') as f:
        t = json.load(f)
        proxy_array = [ProxyServer(i, client_array)
                       for i, value in enumerate(t)]

    """
    p = [Process(target=proxy.bet) for proxy in proxy_array]

    for proc in p:
        proc.start()
    for proc in p:
        proc.join()
    """

    with Pool(processes=len(proxy_array)) as p:
        localpayment = list(p.map(ProxyServer.bet, proxy_array))
        if len(localpayment) == 1:
            localpayment = localpayment[0]
        if len(localpayment) >= 2:
            localpayment = dict(chain([x.items() for x in localpayment]))

    if time.time() - duration >= 1:
        logging.getLogger("all_bet").info(
            f"executed in {time.time() - duration}")

    payment[NAME] = localpayment

# ----------------------------------------------
# specific functions

def init_config(mode=''):
    if mode == 'find_matches':
        driver = bet_manage.create_webdriver(
            profile_path='/home/smaking/.mozilla/firefox/rwythdx5.default-release')

    else:
        driver = bet_manage.create_webdriver()
    return driver

