import nltk
import re
from moduls import bet_manage

# templates parsing

OFFSET_TABLE = {
    'Карта Победа' : 'map_winner',
    'Победа в матче' : 'game_winner',
}

def find_vs(words, idx) :
    right_team = ''
    left_team = ''
    ndx = idx + 1
    while (re.search('[A-Za-z0-9\']+', words[ndx]) and words[ndx].find(':') < 0) :
        if (right_team.upper().find(words[ndx].upper()) < 0) :
            right_team = right_team + ' ' + words[ndx]
            ndx += 1
        else :
            break

    ndx = idx - 1
    while (re.search('[A-Za-z0-9\']+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0) :
        if (left_team.upper().find(words[ndx].upper()) < 0) :
            left_team = words[ndx] + ' ' + left_team
            ndx -= 1
        else :
            break

    return left_team + words[idx] + right_team
def find_winner(words, start_idx, match_title) :
    ndx = start_idx - 1
    result = words[ndx]
    lst_word = words[ndx]
    ndx -= 1
    while (re.search('[A-Za-z0-9]+', words[ndx]) and ndx >= 0 and words[ndx].find(':') < 0) :
        if (match_title.find(words[ndx]) and lst_word != words[ndx]) :
            result = words[ndx] + ' ' + result
            lst_word = words[ndx]
            ndx -= 1
        else :
            break
    return result

def template1(text) :
    temp = [
        'ПОБЕДА НА КАРТЕ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse1(photo_url, words) :
    dic = {}
    dic['match_title'] = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        dic['winner'] = dic['match_title'][: dic['match_title'].find('vs') - 1]
    elif (side == 'right') :
        dic['winner'] = dic['match_title'][dic['match_title'].find('vs') + 3 : ]

    dic['outcome_index'] = ('map_winner', words[words.index('#') + 1])

    return dic

def template2(text) :
    temp = [
        'ПОБЕДА\s+В\s+МАТЧЕ',
        'ОТМЕНИТЬ\s+СТАВКУ',
    ]
    not_temp = [

    ]

    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse2(photo_url, words) :
    bet = {}
    bet['match_title'] = find_vs(words, words.index('vs'))

    side = bet_manage.define_side_winner(photo_url)
    if (side == 'left') :
        bet['winner'] = bet['match_title'][: bet['match_title'].find('vs') - 1]
    elif (side == 'right') :
        bet['winner'] = bet['match_title'][bet['match_title'].find('vs') + 3 : ]

    bet['outcome_index'] = OFFSET_TABLE['Победа в матче']

    return bet
    
PHOTO_PARSING_TEMPLATES = [
    (template1, parse1),
    (template2, parse2),
]

# betting process

def find_bet(stavka) :
    # возвращает ссылку на матч
    pass

def make_bet(stavka, match_url) :
    # делает ставку 
    pass
