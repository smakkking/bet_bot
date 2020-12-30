import re
import time
from datetime import datetime, timedelta

from dateutil import parser
import bet_manage
from global_constants import SERVER_DATA_PATH

import selenium.common.exceptions as selen_exc

# управляющие константы, для других модулей
NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'
HAS_API = False
TAKES_MATCHES_LIVE = False
MATCHES_UPDATE_TIMEh = 8
LIVE_MATCHES_UPDATE_TIMEh = 1

# менять, когда меняешь сеть, см в куках
CURRENT_CF_CLEARANCE = '366d5424a19b0f1809696a3f73871cb8682e1de0-1609339139-0-150'

OFFSET_TABLE = {
    'Победа на карте' : 'map_winner',
    'Победа в матче' : 'game_winner',
    'Количество раундов' : 'total_score'
}

# templates parsing

def find_vs(words : list, idx : int) :
    right_team = ''
    left_team = ''
    ndx = idx + 1
    while (re.search('[A-Za-z0-9\']+', words[ndx]) and words[ndx].find(':') < 0) :
        if (right_team.upper().find(words[ndx].upper()) < 0) :
            right_team = right_team + ' ' + words[ndx]
            ndx += 1
        else :
            break

    ndx = idx - 1
    while (re.search('[A-Za-z0-9\']+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0) :
        if (left_team.upper().find(words[ndx].upper()) < 0) :
            left_team = words[ndx] + ' ' + left_team
            ndx -= 1
        else :
            break

    return bet_manage.reform_team_name(left_team) + ' vs ' + bet_manage.reform_team_name(right_team)
def find_winner(words : list, start_idx : int, match_title : str) :
    ndx = start_idx - 1
    result = words[ndx]
    lst_word = words[ndx]
    ndx -= 1
    while (re.search('[A-Za-z0-9]+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0) :
        if (match_title.find(words[ndx]) and lst_word != words[ndx]) :
            result = words[ndx] + ' ' + result
            lst_word = words[ndx]
            ndx -= 1
        else :
            break
    return result

def template1(text : str) :
    temp = [
        r'ПОБЕДА\s*НА\s*КАРТЕ',
        r'ОТМЕНИТЬ\s*СТАВКУ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse1(photo_url : str, words : list) :
    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 : ]
    res.outcome_index = (OFFSET_TABLE['Победа на карте'], int(words[words.index('#') + 1]))

    return res

def template2(text : str) :
    temp = [
        # добавить \s*
        r'ПОБЕДА\s*В\s*МАТЧЕ',
        r'ОТМЕНИТЬ\s*СТАВКУ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)

    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse2(photo_url : str, words : list) :

    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 :]
    res.outcome_index = OFFSET_TABLE['Победа в матче']

    return res

PHOTO_PARSING_TEMPLATES = [
    (template1, parse1),
    (template2, parse2),
]

def find_bet(last_date, update_live=False, update_all=False) :
    # TODO exceptions and logging

    xPath_matches = '//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div'

    browser = init_config()
    # тест
    bet_manage.get_html_with_browser(browser, WALL_URL, sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE), ])
    bbb = {}
    matches = browser.find_elements_by_xpath(xPath_matches)

    for a in matches :
        if a == matches[len(matches) - 1] or a.text == 'Нет активных матчей':
            continue
        try :
            begin = datetime.strptime(a.find_element_by_class_name('sys-datetime').text, '%d.%m %H:%M')
        except ValueError :
            begin = datetime.strptime(a.find_element_by_class_name('sys-datetime').text, '%H:%M')
            begin = begin.replace(day=datetime.now().day, month=datetime.now().month)
        begin =begin.replace(year=datetime.now().year) # здесь приходится поправлять каждый год

        event_info = {}

        left_team   = a.find_element_by_class_name('bet-team_left ').find_element_by_class_name('bet-team__name')
        right_team  = a.find_element_by_class_name('bet-team_right ').find_element_by_class_name('bet-team__name')

        event_info['begin_date'] = begin.isoformat()
        event_info['team1'] = bet_manage.reform_team_name(left_team.text.replace(left_team.find_element_by_tag_name('div').text, ''))
        event_info['team2'] = bet_manage.reform_team_name(right_team.text.replace(right_team.find_element_by_tag_name('div').text, ''))

        bbb[a.find_element_by_class_name('sys-matchlink').get_attribute('href')] = event_info


    new_data = []
    for match in last_date :
        if datetime.now() - parser.parse(match['begin_date']) > timedelta(hours=3):
            continue
        elif (update_live and parser.parse(match['begin_date']) < datetime.now()) or update_all :
            match['outcomes'] = {}
            bet_manage.get_html_with_browser(browser, match['link'])
            # победа
            try :
                t1 = browser.find_element_by_xpath('//*[@id="sys-container"]/div[2]')
                match['outcomes'][OFFSET_TABLE['Победа в матче']] = t1.get_attribute('data-id')
            except :
                pass

            # доп события
            t2 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[1]/div[2]/div')
            if t2 != [] :
                for x in t2:
                    for title in OFFSET_TABLE.keys():
                        if x.find_element_by_class_name('bma-title').text.find(title) >= 0:
                            match['outcomes'][OFFSET_TABLE[title]] = x.get_attribute('data-id')

            # карта 1
            t31 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[2]/div[2]/div')
            if t31 != [] :
                match['outcomes']['map1'] = {}
                for x in t31 :
                     for title in OFFSET_TABLE.keys() :
                        if x.find_element_by_class_name('bma-title').text.find(title) >= 0 :
                            match['outcomes']['map1'][OFFSET_TABLE[title]] = x.get_attribute('data-id')
            # карта 2
            t32 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[3]/div[2]/div')
            if t32 != []:
                match['outcomes']['map2'] = {}
                for x in t32 :
                     for title in OFFSET_TABLE.keys() :
                        if x.find_element_by_class_name('bma-title').text.find(title) >= 0 :
                            match['outcomes']['map2'][OFFSET_TABLE[title]] = x.get_attribute('data-id')
            # карта 3
            t33 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[4]/div[2]/div')
            if t33 != []:
                    match['outcomes']['map3'] = {}
                    for x in t33 :
                         for title in OFFSET_TABLE.keys() :
                            if x.find_element_by_class_name('bma-title').text.find(title) >= 0 :
                                match['outcomes']['map3'][OFFSET_TABLE[title]] = x.get_attribute('data-id')
            del bbb[match['link']]
        new_data.append(match)

    for match_key in bbb.keys() :
        match = bbb[match_key]
        match['link'] = match_key
        match['outcomes'] = {}
        bet_manage.get_html_with_browser(browser, match_key)
        # победа
        try:
            t1 = browser.find_element_by_xpath('//*[@id="sys-container"]/div[2]')
            match['outcomes'][OFFSET_TABLE['Победа в матче']] = t1.get_attribute('data-id')
        except:
            pass

        # доп события
        t2 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[1]/div[2]/div')
        if t2 != []:
            for x in t2:
                for title in OFFSET_TABLE.keys():
                    if x.find_element_by_class_name('bma-title').text.find(title) >= 0:
                        match['outcomes'][OFFSET_TABLE[title]] = x.get_attribute('data-id')

        # карта 1
        t31 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[2]/div[2]/div')
        if t31 != []:
            match['outcomes']['map1'] = {}
            for x in t31:
                for title in OFFSET_TABLE.keys():
                    if x.find_element_by_class_name('bma-title').text.find(title) >= 0:
                        match['outcomes']['map1'][OFFSET_TABLE[title]] = x.get_attribute('data-id')
        # карта 2
        t32 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[3]/div[2]/div')
        if t32 != []:
            match['outcomes']['map2'] = {}
            for x in t32:
                for title in OFFSET_TABLE.keys():
                    if x.find_element_by_class_name('bma-title').text.find(title) >= 0:
                        match['outcomes']['map2'][OFFSET_TABLE[title]] = x.get_attribute('data-id')
        # карта 3
        t33 = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div[4]/div[2]/div')
        if t33 != []:
            match['outcomes']['map3'] = {}
            for x in t33:
                for title in OFFSET_TABLE.keys():
                    if x.find_element_by_class_name('bma-title').text.find(title) >= 0:
                        match['outcomes']['map3'][OFFSET_TABLE[title]] = x.get_attribute('data-id')

    browser.close()
    browser.quit()

    new_data.extend(bbb.values())
    return new_data

# betting process

def make_bet(stavka, summ, session_key='fghfh12wafsd') :
    # если ставка на доту - то betsdota2.fun
    #base_str = 'https://betscsgo.in/index/placebet/'

    base_str = stavka.bk_links[NAME]['link'][ :stavka.bk_links[NAME]['link'].find('match')] + 'index/placebet/'

    # здесь формируем запрос
    base_str += stavka.bk_links[NAME]['bet_id'] + '/'

    # не раб с больше\меньше
    if stavka.bk_links[NAME]['team1'] == stavka.winner :
        base_str += '1/'
    elif stavka.bk_links[NAME]['team2'] == stavka.winner :
        base_str += '2/'

    base_str += str(summ) + '/' + session_key
    return base_str


def init_config(chrome_dir_path=None) :
    # о структуре словаря см scan_database.py
    if chrome_dir_path is None :
        driver = bet_manage.create_webdriver()
    else :
        driver = bet_manage.create_webdriver(user_id=chrome_dir_path)
    return driver


def login(chdp=None, bkm_login=None, bkm_password=None) :
    # аккаунт должен быть без steam_guard

    # на вход подается запись из таблицы бд со всеми доступными полями(доступ по .)

    # TODO exceptions and logging

    browser = init_config(chdp)
    bet_manage.get_html_with_browser(browser, WALL_URL, sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE), ])

    btn = browser.find_element_by_xpath('/html/body/div/div[3]/header/div[1]/div/div[2]/div[2]/div/div[2]/a')
    btn.click()

    login_form = browser.find_element_by_xpath('//*[@id="steamAccountName"]')
    pass_form =  browser.find_element_by_xpath('//*[@id="steamPassword"]')

    login_form.send_keys(bkm_login)
    pass_form.send_keys(bkm_password)

    browser.find_element_by_xpath('//*[@id="imageLogin"]').click()

    time.sleep(5)
    browser.close()
    browser.quit()


def dogon_check(stavka) :
    browser = init_config()

    bet_manage.get_html_with_browser(browser, stavka.bk_links[NAME]['link'], sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE)])

    alloutcomes_xPath = '//*[@id="bm-additionals"]/div[' + str(stavka.outcome_index[1] + 1) + ']/div[2]/div'
    outcomes = browser.find_elements_by_xpath(alloutcomes_xPath)

    for out in outcomes :
        if out.get_attribute('class').find('has-score') >= 0:
            event = OFFSET_TABLE['Победа на карте']
        else :
            event = OFFSET_TABLE[out.find_element_by_class_name('bma-title').text]
        btns = out.find_elements_by_tag_name('button')

        if event == stavka.outcome_index[0] :
            winner = None
            if btns[0].value_of_css_property('color') == 'rgba(86, 115, 10, 1)':
                winner = bet_manage.reform_team_name(btns[0].text[btns[0].text.find('\n') + 1:])
            elif btns[1].value_of_css_property('color') == 'rgba(86, 115, 10, 1)':
                winner = bet_manage.reform_team_name(btns[1].text[btns[1].text.find('\n') + 1:])

            browser.close()
            browser.quit()

            if winner :
                if winner == stavka.winner :
                    return True
                else :
                    return False
            else :
                return None

