import undetected_chromedriver as uc
import time

opts = uc.ChromeOptions()
opts.add_argument('--user-data-dir=' + r'C:\Users\user1\AppData\Local\Google\Chrome\ID_102')
opts.add_argument('--profile-directory=Profile1')

def qautra(i) :
    
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
    return bbb[i]

def make_b(stavka, match_url) :
    driver = uc.Chrome(options=opts, enable_console_log=True)
    driver.get(match_url)
    driver.add_cookie({'name' : 'cf_clearance', 'value' : '609e09155652a528ec720157decb827b12bb7fb1-1605276868-0-1z20a49547z9321ccadz91a5e051-150'})
    # выработка купона
    time.sleep(10)
    if stavka['match_outcome'] == 'game_winner' :
        win_btns = driver.find_elements_by_xpath('//*[@id="sys-container"]/div[2]/div/div/button')
        #print(win_btns[0].text)
        #print(win_btns[1].text)
        if win_btns[0].text.find(stavka['winner']) >= 0 :
            win_btns[0].click()
        elif win_btns[1].text.find(stavka['winner']) >= 0 :
            win_btns[0].click()
    elif stavka['match_outcome'] is tuple and stavka['match_outcome'][0] == 'map_winner' :
        win_btns = driver.find_elements_by_xpath('//*[@id="bm-additionals"]/div/div/div/div/div/button')
        map_number = int(stavka['match_outcome'][1])
        if win_btns[2 * (map_number - 1)].text.find(stavka['winner']) >= 0 :
            win_btns[2 * (map_number - 1)].click()
        elif win_btns[1 + 2 * (map_number - 1)].text.find(stavka['winner']) >= 0:
            win_btns[1 + 2 * (map_number - 1)].click()
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/input').send_keys(stavka['summ'])
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div[2]/div[2]/div[3]/div[3]/div/button').click()

    # искать поле, куда вбивать

if __name__ == "__main__":
    make_b({
        'match_outcome' : 'game_winner',
        'winner' : 'Downfall',
        'summ' : '1'
    }, 'https://betscsgo.in/match/256831/')
    



    