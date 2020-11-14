import nltk
import re
import time
from moduls import bet_manage

# templates parsing
NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'

CURRENT_CF_CLEARANCE = '609e09155652a528ec720157decb827b12bb7fb1-1605276868-0-1z20a49547z9321ccadz91a5e051-150'

OFFSET_TABLE = {
    'Карта Победа' : 'map_winner',
    'Победа в матче' : 'game_winner',
}

def find_vs(words, idx) :
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

    return left_team + words[idx] + right_team
def find_winner(words, start_idx, match_title) :
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

def template1(text) :
    temp = [
        'ПОБЕДА НА КАРТЕ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse1(photo_url, words) :
    dic = {}
    dic['match_title'] = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        dic['winner'] = dic['match_title'][: dic['match_title'].find('vs') - 1]
    elif (side == 'right') :
        dic['winner'] = dic['match_title'][dic['match_title'].find('vs') + 3 : ]

    dic['outcome_index'] = ('map_winner', words[words.index('#') + 1])

    return dic

def template2(text) :
    temp = [
        'ПОБЕДА\s+В\s+МАТЧЕ',
        'ОТМЕНИТЬ\s+СТАВКУ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse2(photo_url, words) :
    bet = {}
    bet['match_title'] = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        bet['winner'] = bet['match_title'][: bet['match_title'].find('vs') - 1]
    elif (side == 'right') :
        bet['winner'] = bet['match_title'][bet['match_title'].find('vs') + 3 : ]

    bet['outcome_index'] = OFFSET_TABLE['Победа в матче']

    return bet
    
PHOTO_PARSING_TEMPLATES = [
    (template1, parse1),
    (template2, parse2),
]

# betting process

def find_bet(browser, stavka) -> str:
    # возвращает ссылку на матч
    # на вход подается браузер + объект класса Stavka

    xPath_matches = '//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div'

    bet_manage.get_html_with_browser(browser, WALL_URL, 2)
    browser.add_cookie({'name' : 'cf_clearance', 'value' : CURRENT_CF_CLEARANCE})
    time.sleep(10) # подумать над временем ожидания
    bbb = []
    matches = browser.find_elements_by_xpath(xPath_matches)
    try :
        for a in matches :
            if a == matches[len(matches) - 1] :
                continue
            left_team = a.find_element_by_class_name('bet-team_left').find_element_by_class_name('bet-team__name')
            right_team = a.find_element_by_class_name('bet-team_right').find_element_by_class_name('bet-team__name')
            bbb.append({
                'link' : a.find_element_by_class_name('sys-matchlink').get_attribute('href'),
                'match_name' : left_team.text.replace(left_team.find_element_by_tag_name('div').text, '') + ' | ' + right_team.text.replace(right_team.find_element_by_tag_name('div').text, '')
            })
    except Exception:
        # проблема - не закрываются браузеры(точнее закрываются, но из-за этого ничего не работает)
        print('unpredictable error... STOP!')
    for b in bbb :
        if b['match_name'] == stavka.match_title :
            return b['link']
    return 'not_valid'


# нужна функция логина!!!!!!!!!!!!!!

def make_bet(browser, stavka, match_url) :
    # делает ставку 
    bet_manage.get_html_with_browser(browser, match_url, 1)
    
    pass
