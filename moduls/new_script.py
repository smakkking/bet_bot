import sys

from selenium import webdriver
from datetime import datetime

import time
from datetime import datetime



from . import manage_file
from moduls.bookmaker_moduls import parimatch_betting
from moduls.group_moduls import rushBet_group

def main() :
    # запускаем браузер
    BROWSER = manage_file.create_webdriver()

    group_photo = {'rB' : {}, 'mmrD' : {}, 'rBp' : {}}
    cycle_encounter = 0
    while (True) :
        group_photo['rB'] = rushBet_group.main_script(BROWSER, group_photo['rB'], cycle_encounter)
        cycle_encounter += 1
    BROWSER.quit()
    sys.exit()
    
if __name__ == '__main__' :
    main()