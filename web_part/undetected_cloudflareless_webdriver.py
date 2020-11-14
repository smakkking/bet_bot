import undetected_chromedriver as uc
import time

#specify chromedriver version to download and patch
uc.TARGET_VERSION = 86   

# or specify your own chromedriver binary (why you would need this, i don't know)

uc.install(
    executable_path='c:/GitRep/bet_bot/chromedriver.exe',
)

opts = uc.ChromeOptions()
#opts.add_argument('--user-data-dir=' + r'C:\Users\user1\AppData\Local\Google\Chrome\User Data')
#opts.add_argument('--profile-directory=Profile 1')

#xPath_matchesfuture = '/html/body/div/div[4]/div/div/div[2]/div[1]/div[1]/div[2]/div[1]'

def qautra(i) :
    driver = uc.Chrome(options=opts, enable_console_log=True)
    driver.get('https://betscsgo.in') 
    driver.add_cookie({'name' : 'cf_clearance', 'value' : '609e09155652a528ec720157decb827b12bb7fb1-1605276868-0-1z20a49547z9321ccadz91a5e051-150'})
    time.sleep(10)
    bbb = []
    aaa = driver.find_elements_by_xpath('//*[@id="bets-block"]/div[1]/div[2]/div/div/div/div')

    for a in aaa :
        if a == aaa[len(aaa) - 1] :
            continue
        left_team = a.find_element_by_class_name('bet-team_left').find_element_by_class_name('bet-team__name')
        right_team = a.find_element_by_class_name('bet-team_right').find_element_by_class_name('bet-team__name')
        bbb.append({
            'link' : a.find_element_by_class_name('sys-matchlink').get_attribute('href'),
            'match_name' : left_team.text.replace(left_team.find_element_by_tag_name('div').text, '') + ' | ' + right_team.text.replace(right_team.find_element_by_tag_name('div').text, '')
        })
    return bbb[7]

def make_b() :
    driver = uc.Chrome(options=opts, enable_console_log=True)
    driver.get('https://betscsgo.in/match/256486/')
    driver.add_cookie({'name' : 'cf_clearance', 'value' : '609e09155652a528ec720157decb827b12bb7fb1-1605276868-0-1z20a49547z9321ccadz91a5e051-150'})
    #time.sleep(60)

if __name__ == "__main__":
    driver = uc.Chrome(options=opts, enable_console_log=True)
    driver.get('https://betscsgo.in/match/256455/')
    driver.add_cookie({'name' : 'cf_clearance', 'value' : '609e09155652a528ec720157decb827b12bb7fb1-1605276868-0-1z20a49547z9321ccadz91a5e051-150'})
    stavka = {} 
    # выработка купона
    if stavka['match_outcome'] == 'game_winner' :
        win_btns = driver.find_elements_by_xpath('//*[@id="sys-container"]/div[2]/div/div/button')
        if win_btns[0].text == stavka['winner'] :
            win_btns[0].click()
        elif win_btns[1].text == stavka['winner'] :
            win_btns[0].click()
    elif stavka['match_outcome'] is tuple and stavka['match_outcome'][0] == 'map_winner' :
        win_btns = driver.find_elements_by_xpath('//*[@id="bm-additionals"]/div/div/div/div/div/button')
        map_number = int(stavka['match_outcome'][1])
        if (win_btns[2 * (map_number - 1)].text == stavka['winner']) :
            win_btns[2 * (map_number - 1)].click()
        elif (win_btns[1 + 2 * (map_number - 1)].text == stavka['winner']) :
            win_btns[1 + 2 * (map_number - 1)].click()
    



    