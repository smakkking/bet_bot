import nltk
import re

OFFSET_TABLE = {
    'Победа в матче' : 'match_win',
    'Карта Победа' : 'map_win'
}

def find_vs(words, idx) :
    right_team = ''
    left_team = ''
    ndx = idx + 1
    while (re.search('[A-Za-z\']+', words[ndx])) :
        if (right_team.upper().find(words[ndx].upper()) < 0) :
            right_team = right_team + ' ' + words[ndx]
            ndx += 1
        else :
            break

    ndx = idx - 1
    while (re.search('[A-Za-z\']+', words[ndx]) and ndx >= 0) :
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
    while (re.search('[A-Za-z]+', words[ndx]) and ndx >= 0) :
        if (match_title.find(words[ndx]) and lst_word != words[ndx]) :
            result = words[ndx] + ' ' + result
            lst_word = words[ndx]
            ndx -= 1
        else :
            break
    return result

def tmp1(text) :
    temp = [
        '\[Карта\s#\d]\s+Победа',
        'Ставка\s+сделана',
    ]
    not_temp = [
        'Выигрыш',
        'Проигрыш',
    ]
    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse1(words) :
    dic1 = {}
    map_index = words.index('Карта')

    dic1['match_title'] = find_vs(words, words.index('vs'))
    
    dic1['winner'] = words[words.index('[') - 1]
    dic1['outcome_index'] = ('map_winner', words[words.index('#') + 1])

    return dic1

def tmp2(text) :
    temp = [
        'Победа\s+в\s+матче',
        'Ставка\s+сделана',
    ]
    not_temp = [
        'Выигрыш',
        'Проигрыш'
    ]
    flag = True
    for x in temp :
        flag = flag and re.search(x, text)
    for x in not_temp :
        flag = flag and text.find(x) < 0
    return flag
def parse2(words) :
    dic = {}
    dic['match_title'] = find_vs(words, words.index('vs'))

    dic['winner'] = find_winner(words, words.index('Победа'), dic['match_title'])
    dic['outcome_index'] = OFFSET_TABLE['Победа в матче']

    return dic

BET_TEMPLATES = [
    (tmp1, parse1),
    (tmp2, parse2),
]
    

