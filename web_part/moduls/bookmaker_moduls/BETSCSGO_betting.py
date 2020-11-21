import nltk
import re
import time
from moduls import bet_manage

NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'

CURRENT_CF_CLEARANCE = 'e112a88f17bfc124538aa73d04eca7193e5ad1f6-1605892639-0-150'

OFFSET_TABLE = {
    'Карта Победа' : 'map_winner',
    'Победа в матче' : 'game_winner',
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

    return left_team + words[idx] + right_team
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
def parse1(photo_url : str, words : list) :
    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 : ]
    res.outcome_index = ('map_winner', words[words.index('#') + 1])

    return res

def template2(text : str) :
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
def parse2(photo_url : str, words : list) :

    res = bet_manage.Stavka()
    res.match_title = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        res.winner = res.match_title[: res.match_title.find('vs') - 1]
    elif (side == 'right') :
        res.winner = res.match_title[res.match_title.find('vs') + 3 : ]
    res.outcome_index = OFFSET_TABLE['Победа в матче']

    return res
    
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
    browser.add_cookie({
        'name' : 'cf_clearance',
        'value' : CURRENT_CF_CLEARANCE
    })
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

def make_bet(browser, stavka, match_url, bet_summ) :
    # делает ставку 
    bet_manage.get_html_with_browser(browser, match_url)
    browser.add_cookie({
        'name' : 'cf_clearance', 
        'value' : CURRENT_CF_CLEARANCE
    })
    time.sleep(5) # подумать над временем ожидания

    xPath_summinput = '/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/input'
    xPath_bet = '/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[3]/div[3]/div/button'

    # подумать над более эффективной обработке
    if stavka.match_outcome == OFFSET_TABLE['Победа в матче'] :
        win_btns = browser.find_elements_by_xpath('//*[@id="sys-container"]/div[2]/div/div/button')
        if win_btns[0].text.find(stavka['winner']) >= 0 :
            win_btns[0].click()
        elif win_btns[1].text.find(stavka['winner']) >= 0 :
            win_btns[0].click()
    elif stavka['match_outcome'] is tuple and stavka['match_outcome'][0] == OFFSET_TABLE['Карта Победа'] :
        win_btns = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div/div/div/div/div/button')
        map_number = int(stavka['match_outcome'][1])
        if win_btns[2 * (map_number - 1)].text.find(stavka['winner']) >= 0 :
            win_btns[2 * (map_number - 1)].click()
        elif win_btns[1 + 2 * (map_number - 1)].text.find(stavka['winner']) >= 0:
            win_btns[1 + 2 * (map_number - 1)].click()
    time.sleep(1) # подумать над временем ожидания
    
    browser.find_element_by_xpath(xPath_summinput).send_keys(bet_summ)
    time.sleep(1) # подумать над временем ожидания
    browser.find_element_by_xpath(xPath_bet).click()

def init_config(single_user_data=None) :
    # о структуре словаря см scan_database.py
    if single_user_data == None :
        driver = bet_manage.create_webdriver(undetected_mode=True)
    else :
        driver = bet_manage.create_webdriver(user_id=single_user_data['chrome_dir_path'], undetected_mode=True)
    return driver
