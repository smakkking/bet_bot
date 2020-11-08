from moduls import bet_manage
import time

WALL_URL = 'https://vk.com/akademiya_stavki_csgo'
NAME = 'AcademiaStavok'

def template1(text) :
    flag = True
    try :
        flag = flag and text[4] == 'vs'
        flag = flag and text[len(text) - 1] == 'ОТМЕНИТЬ СТАВКУ'
    except IndexError :
        flag = False
    return flag

def parse1(photo_url, text) :
    bet = {}

    bet['match_title'] = text[1].replace('vs', '-')
    bet['summ'] = 20.0

    side = bet_manage.define_side_winner(photo_url)
    if side == 'left' :
        bet['winner'] = text[6]
    elif side == 'right' :
        bet['winner'] = text[7]
    
    for key in OFFSET_TABLE.keys() :
        if text[2].find(key) != -1 :
            if OFFSET_TABLE[key].find('map') != -1 :
                pos = text[2].find('#')
                map_number = int(text[2][pos + 1])
                bet['outcome_index'] = (text[2][pos + 4 : ], map_number)
            else :
                bet['outcome_index'] = text[2]
    return bet

BET_TEMPLATES = [
    (template1, parse1),
]
OFFSET_TABLE = {
    # победитель по карте
        'ПОБЕДА НА КАРТЕ' : 'map_winner',
    # победа команды
        'ПОБЕДА В МАТЧЕ' : 'match_result',
}

