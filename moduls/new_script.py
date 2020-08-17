from selenium import webdriver
from datetime import datetime
import sys
import time
from datetime import datetime



import manage_file
# bk
import parimatch_betting
# groups
import rushBet_group
import rushBetPrivate_group
import mmrDauns_group

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