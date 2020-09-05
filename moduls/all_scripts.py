from selenium import webdriver
from datetime import datetime

import time
import json
import sys
from datetime import datetime

from moduls import bet_manage
from moduls.group_moduls import AcademiaStavok_group, CSgoNorch_group, CSgoVictory_group 
from manage import ALL_POSTS_JSON_PATH, CHROME_DIR_PACKAGES

GROUP_OFFSET = {
    'AcademiaStavok' : AcademiaStavok_group,
    'CSgoNorch' : CSgoNorch_group,
    'CSgoVictory' : CSgoVictory_group,
}

def checking_for_bets(user, data) :
    browser = bet_manage.create_webdriver(CHROME_DIR_PACKAGES + r'\ID_' + user.chrome_dir_path)
    for key in data.keys() :
        if data[key] == 'old' or key == 'open_browser':
            continue
        pst = bet_manage.GroupInfoPost(data[key])
        obj = pst.pasrering(browser, GROUP_OFFSET[key])
        # здесь поидее обработка ошибки, если пост не ставка
        # а также процесс ставки на букмекерке
        if obj.bets :
            # тут как раз весь процесс
            data[key] = 'ok'
        else :
            data[key] = 'not bet'
    browser.close()
    browser.quit()
    
def load_last_data() :
    browser = bet_manage.create_webdriver()
    data = {}
    try :
        for (group_name, group) in GROUP_OFFSET.items() :
            post = bet_manage.LastGroupPost()
            post.get(browser, group.WALL_URL)
            data[group_name] = post.__json_repr__()
    finally :
        browser.close()
        browser.quit() 
        with open(ALL_POSTS_JSON_PATH, 'w') as last_posts_json : 
            json.dump(data, last_posts_json, indent=4)

if __name__ == '__main__' :
    pass