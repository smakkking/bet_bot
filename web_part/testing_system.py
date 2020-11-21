# здесь тестируем все модули по группам и букмекеркам

import manage
from moduls.bet_manage import get_text_from_image, create_webdriver, get_html_with_browser, Stavka

from moduls.group_moduls import CSgoVictory_group
from moduls.bookmaker_moduls import BETSCSGO_betting
from manage import BET_PROJECT_ROOT, ALL_POSTS_JSON_PATH
import nltk
import time
import json


def testing_group() :
    images_array = [
        'https://sun9-32.userapi.com/-ab-W8ZmG-MtryE8cn8rPOro-HndYWgdSFlZrQ/NZ1aNgG1IqM.jpg',
    ]
    browser = create_webdriver()
    try :
        leng = 0
        for x in images_array :
            now = time.time()
            leng += 1
            text = '\n'.join(get_text_from_image(browser, x))
            flag = False
            for (tmp, par) in CSgoVictory_group.BET_TEMPLATES :
                if (tmp(text)) :
                    print(par(x, nltk.word_tokenize(text))) 
                    flag = True
            assert flag, 'FAILED ON TEST {}'.format(leng) 
            print(f'{time.time() - now} seconds spent on test_{leng}')
        print('ALL {} TESTS ARE CLEAR!'.format(leng))
    finally :
        browser.close()
        browser.quit()
    
if __name__ == "__main__" :
    browser = BETSCSGO_betting.init_config()
    BETSCSGO_betting.find_bet(browser, Stavka())
    browser.close()
    browser.quit()

