# строка для правильной работы импортирования пакетов
import sys
sys.path[0] = sys.path[0][ : sys.path[0].find('bet_bot') + 7]

from moduls import manage_file
import time

LAST_DATA = manage_file.LastGroupPost(wall_url='https://vk.com/csgo_norch')

def template1(text) :
    flag = True
    flag = flag and len(text) == 8
    flag = flag and text[4] == 'Общая ставка:'
    flag = flag and text[5] == 'заплатит:'
    return flag

def parse1(text) :
    bet = {}
    
    # фикс бага в распознавании
    text[0]= text[0].replace('V3 ', '')
    text[1]= text[1].replace('V3 ', '')

    bet['match_title'] = text[0] + ' - ' + text[1]
    bet['summ'] = 20.0
    for key in offset_table.keys() :
        if text[2].find(key) :
            bet['outcome_index'] = offset_table[key]
            text[2] = text[2].replace(key + ' ', '')
            break
    # не работает с форой
    bet['winner'] = text[2]

BET_TEMPLATES = [
    (template1, parse1),
]

offset_table = {
    'ПОБЕДИТЕЛЬ МАТЧА' : 'match_result',
    'ПОБЕДИТЕЛЬ 1 КАРТЫ' : ('map_winner', 1),
    'ПОБЕДИТЕЛЬ 2 КАРТЫ' : ('map_winner', 2),
    'ПОБЕДИТЕЛЬ 3 КАРТЫ' : ('map_winner', 3),
    'ПОБЕДИТЕЛЬ 4 КАРТЫ' : ('map_winner', 4),
    'ПОБЕДИТЕЛЬ 5 КАРТЫ' : ('map_winner', 5),
    'Фора карт' : 'map_handicap'
}

if __name__ == "__main__":
    pass






