# строка для правильной работы импортирования пакетов
import sys
sys.path[0] = sys.path[0][ : sys.path[0].find('bet_bot') + 7]

from moduls import manage_file
import time

WALL_URL = 'https://vk.com/victorybets_stavki'

def template1(text) :
    flag = True
    flag = flag and text[4] == 'vs'
    flag = flag and text[len(text) - 1] == 'ОТМЕНИТЬ СТАВКУ'
    return flag

def parse1(photo_url, text) :
    bet = {}

    bet['match_title'] = text[1].replace('vs', '-')
    bet['summ'] = 20.0

    side = manage_file.define_side_winner(photo_url)
    if side == 'left' :
        bet['winner'] = text[6]
    elif side == 'right' :
        bet['winner'] = text[7]
    
    for key in offset_table.keys() :
        if text[2].find(key) != -1 :
            if offset_table[key].find('map') != -1 :
                pos = text[2].find('#')
                map_number = int(text[2][pos + 1])
                bet['outcome_index'] = (text[2][pos + 4 : ], map_number)
            else :
                bet['outcome_index'] = text[2]
    return bet


BET_TEMPLATES = [
    (template1, parse1),
]
offset_table = {
    # победитель по карте
        'ПОБЕДА НА КАРТЕ' : 'map_winner',
    # победа команды
        'ПОБЕДА В МАТЧЕ' : 'match_result',
}
    
if __name__ == "__main__":
    browser = manage_file.create_webdriver()
    try :
        pass
    finally :
        browser.close()
        browser.quit()
