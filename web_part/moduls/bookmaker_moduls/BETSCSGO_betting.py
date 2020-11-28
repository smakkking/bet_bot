import nltk, re, time, json
from moduls import bet_manage
from manage import BET_PROJECT_ROOT

# управляющие константы, для других модулей
NAME = 'betscsgo'
WALL_URL = 'https://betscsgo.in'
HAS_API = False
TAKES_MATHES_LIVE = False

# менять, когда меняешь сеть, см в куках
CURRENT_CF_CLEARANCE = 'e1c408ca9bebacb24b1e7edc7583a34077e59da5-1606575106-0-150'


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
        'ПОБЕДА\s*НА\s*КАРТЕ',
        'ОТМЕНИТЬ\s*СТАВКУ',
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
    res.outcome_index = (OFFSET_TABLE['Карта Победа'], words[words.index('#') + 1])

    return res

def template2(text : str) :
    temp = [
        # добавить \s*
        'ПОБЕДА\s*В\s*МАТЧЕ',
        'ОТМЕНИТЬ\s*СТАВКУ',
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

def find_bet() :
    # в начале дня собирает инфу о матчах и кладет в словарь

    xPath_matches = '//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div'

    browser = init_config()
    # тест
    bet_manage.get_html_with_browser(browser, WALL_URL, sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE), ])
    bbb = []
    matches = browser.find_elements_by_xpath(xPath_matches)

    # почему-то иногда падает и не ищет left_team и right_team. суууууккаааааааааааааа?????????????????????????????
    try :
        for a in matches :
            if a == matches[len(matches) - 1] :
                continue

            left_team   = a.find_element_by_class_name('bet-team_left ').find_element_by_class_name('bet-team__name')
            right_team  = a.find_element_by_class_name('bet-team_right ').find_element_by_class_name('bet-team__name')
            #print(left_team, right_team)
            bbb.append({
                'link'  : a.find_element_by_class_name('sys-matchlink').get_attribute('href'),
                'team1' : bet_manage.reform_team_name(left_team.text.replace(left_team.find_element_by_tag_name('div').text, '')),
                'team2' : bet_manage.reform_team_name(right_team.text.replace(right_team.find_element_by_tag_name('div').text, '')),
            })
    except Exception as e:
        print(f'unpredictable error {e}... STOP!')

    with open(BET_PROJECT_ROOT + '/web_part/user_data/' + NAME + '.json', 'w') as f :
        json.dump(bbb, f, indent=4)

    #time.sleep(1000)

    browser.close()
    browser.quit()

def make_bet(browser, stavka, match_url) :
    # делает ставку 
    # stavka <--> экземпляр класса Stavka

    bet_manage.get_html_with_browser(browser, match_url, sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE), ])

    xPath_summinput = '/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/input'
    xPath_bet = '/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[3]/div[3]/div/button'

    # подумать над более эффективной обработке
    if stavka.outcome_index == OFFSET_TABLE['Победа в матче'] :
        win_btns = browser.find_elements_by_xpath('//*[@id="sys-container"]/div[2]/div/div/button')
        if bet_manage.reform_team_name(win_btns[0].text).find(stavka.winner) >= 0 :
            win_btns[0].click()
        elif bet_manage.reform_team_name(win_btns[1].text).find(stavka.winner) >= 0 :
            win_btns[0].click()
    elif stavka.outcome_index is tuple and stavka.outcome_index[0] == OFFSET_TABLE['Карта Победа'] :
        win_btns = browser.find_elements_by_xpath('//*[@id="bm-additionals"]/div/div/div/div/div/button')
        map_number = int(stavka.outcome_index[1])
        if bet_manage.reform_team_name(win_btns[2 * (map_number - 1)].text).find(stavka.winner) >= 0 :
            win_btns[2 * (map_number - 1)].click()
        elif bet_manage.reform_team_name(win_btns[1 + 2 * (map_number - 1)].text).find(stavka.winner) >= 0:
            win_btns[1 + 2 * (map_number - 1)].click()
    time.sleep(1) # подумать над временем ожидания
    
    browser.find_element_by_xpath(xPath_summinput).send_keys(stavka.summ)
    time.sleep(1) # подумать над временем ожидания
    browser.find_element_by_xpath(xPath_bet).click()
    time.sleep(1)

def init_config(chrome_dir_path=None) :
    # о структуре словаря см scan_database.py
    if chrome_dir_path == None :
        driver = bet_manage.create_webdriver(undetected_mode=True)
    else :
        driver = bet_manage.create_webdriver(user_id=chrome_dir_path, undetected_mode=True)
    return driver

def login(user) :
    # аккаунт должен быть без steam_guard

    # на вход подается запись из таблицы бд со всеми доступными полями(доступ по .)
    browser = init_config(user.chrome_dir_path)
    bet_manage.get_html_with_browser(browser, WALL_URL, sec=5, cookies=[('cf_clearance', CURRENT_CF_CLEARANCE),])

    # по-другому на вход не пускает - с этим БУДУТ проблемы
    btn = browser.find_element_by_xpath('/html/body/div/div[3]/header/div[1]/div/div[2]/div[2]/div/div[2]/a')
    btn.click()

    login_form = browser.find_element_by_xpath('//*[@id="steamAccountName"]')
    pass_form =  browser.find_element_by_xpath('//*[@id="steamPassword"]')
    
    login_form.send_keys(user.bookmaker_login)
    pass_form.send_keys(user.bookmaker_password)

    browser.find_element_by_xpath('//*[@id="imageLogin"]').click()

    time.sleep(100)
    
    browser.close()
    browser.quit()