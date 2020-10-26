# здесь тестируем все модули по группам и букмекеркам

import manage
from moduls.bet_manage import get_text_from_image, create_webdriver

from moduls.group_moduls import ExpertMnenie_group
from manage import BET_PROJECT_ROOT
import nltk


browser = create_webdriver()

images_array = [
    'https://sun9-3.userapi.com/9TqlmKSUriuufJFzSvXf0n-hl-ibmnsQJJRFSA/VytMqPjsHJQ.jpg',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
]

try :
    leng = 0
    for x in images_array :
        if (x == '') :
            continue
        leng += 1
        text = '\n'.join(get_text_from_image(browser, x))
        flag = False
        for (tmp, par) in ExpertMnenie_group.BET_TEMPLATES :
            if (tmp(text)) :
                print(par(x, nltk.word_tokenize(text))) 
                flag = True
        assert flag, 'FAILED ON TEST {}'.format(leng) 
    print('ALL {} TESTS ARE CLEAR!'.format(leng))
finally :
    browser.close()
    browser.quit()
