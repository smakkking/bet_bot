import time
# ПЕРЕДЕЛАТЬ - УЕБАНЫ НА ПАРИМАТЧ CДЕЛАЛИ НОВУБ ВЕРСИЮ САЙТА БЕЗ ПОИСКА!!!!!!!!!!
import manage_file
import selenium
from selenium.webdriver.support.ui import WebDriverWait

BET_URL = 'https://new.parimatch.ru'

def search_bet(browser, stavka) :
    pass

def bet(browser, stavka) :
    #match_url = search_bet(browser, stavka)
    match_url = 'https://new.parimatch.ru/ru/event/1%7CCS%7Ce1964405daba46d99da77ba5f5046b57%7C1ffa637e9d3c4e018c4c3d3d5848aa29/1%7C5632691'
        
    manage_file.get_html_with_browser(browser, match_url, 12)
    click_on_coupons(browser, stavka)
    # на данном моменте, все нужные купоны уже установлены
    if stavka['type'] == 'ordn' :
        browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[1]')
        fields = browser.find_elements_by_class_name('_3T2hqqpjUHvN6eDM1nHjXI _1dwqB7ix_-iyFwUe7y3gH8 _1RH51R4LOLseaZp2v_ZBZ3')
        for i in range(len(fields)) :
            fields[i].find_element_by_tag_name('input').send_keys(stavka['bets'][i]['summ'])
        browser.find_element_by_class_name('_3y3rrVqaUcKeM8B2xsdUZp').click()
        pass
    elif stavka['type'] == 'expr' :
        browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[2]')
        pass
    elif stavka['type'] == 'sys' :
        browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[3]')
        pass
    
def click_on_coupons(browser, stavka) :
    browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[2]/div[1]').click() #
    time.sleep(6)  
    outcome_array = browser.find_element_by_xpath("/html/body/div[3]/div/div[2]/div[2]").find_elements_by_class_name('TzWpMUHFpcQKGRkjHLBth')                         
    bet_count = 0
    for outcome in outcome_array :
        try :
            outcome.find_element_by_class_name('_13ZKmLYUjuUM095FYb5rbZ') 
        except selenium.common.exceptions.NoSuchElementException:
            outcome.click()
        time.sleep(0.5)
        for bet in stavka['bets'] :
            all_div = outcome.find_elements_by_tag_name('div')
            name = all_div[1].text
            buttons = [div for div in all_div if div.get_attribute('data-id') == 'outcome']
            if spell_check(bet['outcome_index'], name) :
                reform_winner(bet, name)
                for button in buttons :
                    print(button.find_element_by_tag_name('div').text)
                    if button.find_element_by_tag_name('div').text == bet['winner'] :
                        button.click()
                        bet_count += 1
        if bet_count == len(stavka['bets']) :
            break

def reform_winner(bet, name) :
    team1 = bet['match_title'][ : bet['match_title'].find('-') - 1]
    team2 = bet['match_title'][bet['match_title'].find('-') + 2 : ]
    if bet['winner'].find(team1) != -1 :
        bet['winner'] = name[0] + '1' + bet['winner'].replace(team1, '')
    elif bet['winner'].find(team2) != -1 :
        bet['winner'] = name[0] + '2' + bet['winner'].replace(team2, '')
    

def spell_check(info, name) :
    
    offset_table = {
        'map_winner' : 'Победа. Карта',
        'map_handicap' : 'Фора. Карта', 
        'map_total' : 'Тотал. Карта',
        'match_result' : 'Победа',
        'handicap' : 'Фора',
        'score' : 'Счет',
        'total' : 'Тотал',
    }

    if type(info) == tuple and name == offset_table[info[0]] + ' ' + str(info[1]): 
        return True
    if type(info) == str and name == offset_table[info] :
        return True
    return False
    

if __name__ == "__main__":
    browser = manage_file.create_webdriver()
    try :
        bet(browser, {
            'type' : 'ordn',
            'bets' : [
                {
                    'match_title' : 'compLexity - Natus Vincere',
                    'winner' : 'Natus Vincere',
                    'outcome_index' : ('map_winner', 1),
                }
            ]
        })
        pass
    finally :
        browser.close()
        browser.quit()