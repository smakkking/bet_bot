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
    

    
if __name__ == '__main__' :
    pass
    