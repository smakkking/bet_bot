# строка для правильной работы импортирования пакетов
import sys
sys.path[0] = sys.path[0][ : sys.path[0].find('bet_bot') + 7]

from selenium import webdriver
from datetime import datetime

import time
import json
from datetime import datetime

from moduls import manage_file
from moduls.group_moduls import AcademiaStavok_group, CSgoNorch_group, CSgoVictory_group 

GROUP_OFFSET = {
    'AcademiaStavok' : AcademiaStavok_group,
    'CSgoNorch' : CSgoNorch_group,
    'CSgoVictory' : CSgoVictory_group,
}


def checking_for_bets(book_name, data) :
    # решить проблему с браузером
    browser = 1
    for key in data.keys() :
        if data[key] == 'old' :
            continue
        pst = manage_file.GroupInfoPost(data[key])
        obj = pst.pasrering(browser, GROUP_OFFSET[key])
        # здесь поидее обработка ошибки, если пост не ставка
        # а также процесс ставки на букмекерке
        if obj.bets :
            # тут как раз весь процесс
            data[key] = 'ok'
        else :
            data[key] = 'not bet'
    

    
if __name__ == '__main__' :
    #это скрипт для получения последних данных со ВСЕХ групп
    browser = manage_file.create_webdriver()
    data = {}
    try :
        while True :
            post = manage_file.LastGroupPost()
            for group in GROUP_OFFSET.values() :
                post.get(browser, group.WALL_URL)
                data[group.__name__.replace('moduls.group_moduls.', '').replace('_group', '')] = post.__json_repr__()
            last_posts_json = open(sys.path[0] + r'\user_data\group_post_data.json', 'w')
            json.dump(data, last_posts_json, indent=4)
            last_posts_json.close()
    finally :
        last_posts_json.close()
        browser.close()
        browser.quit()
    