# строка для правильной работы импортирования пакетов
import sys
if __name__ == "__main__":
    sys.path.append(r'C:\GitRep\bet_bot')

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

def checking_for_bets(user, data) :
    browser = manage_file.create_webdriver(user.chrome_dir_path)
    for key in data.keys() :
        if data[key] == 'old' or key == 'open_browser':
            continue
        pst = manage_file.GroupInfoPost(data[key])
        obj = pst.pasrering(browser, GROUP_OFFSET[key])
        # здесь поидее обработка ошибки, если пост не ставка
        # а также процесс ставки на букмекерке
        print(obj)
        if obj.bets :
            # тут как раз весь процесс
            data[key] = 'ok'
        else :
            data[key] = 'not bet'
    browser.close()
    browser.quit()
    
def load_last_data() :
    browser = manage_file.create_webdriver()
    data = {}
    try :
        for (group_name, group) in GROUP_OFFSET.items() :
            post = manage_file.LastGroupPost()
            post.get(browser, group.WALL_URL)
            data[group_name] = post.__json_repr__()
    finally :
        browser.close()
        browser.quit() 
        with open(r'C:\GitRep\bet_bot\user_data\group_post_data.json', 'w') as last_posts_json : 
            json.dump(data, last_posts_json, indent=4)

if __name__ == '__main__' :
    load_last_data()
    