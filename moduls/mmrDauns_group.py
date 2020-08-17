import manage_file
import parimatch_betting
import time

COUNT_POSTS = 1
WALL_GET_url = 'https://vk.com/russiandota2pub'

def parse_bet(text) :
    SUMM = 20
    alf_rus = 'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбю'
    alf_eng = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    result = []
    # по 3 строки
    #   match   
    #   outcome_index winner
    #   coeff
    for i in range(0, len(text), 3) :
        pos = 0
        while text[i + 1].find(' ') >= 0 :
            pos0 = text[i + 1].find(' ')
            if alf_rus.find(text[i + 1][pos0 - 1]) >= 0 and alf_eng.find(text[i + 1][pos0 + 1]) >= 0 :
                pos = pos0 
                break
            else :
                text[i + 1].replace(' ', '%', 1)
        text[i + 1].replace('%', ' ')
        result.append({
            'match' : text[i].replace('-', '').replace(' ', '').upper(),
            'winner' : text[i + 1][pos + 1 : len(text[i + 1])],
            'summ' : str(SUMM),
            'outcome_index' : text[i + 1][0 : pos]
        })
    return result

def main_script(BROWSER) :
    photo = manage_file.get_last_post(BROWSER, WALL_GET_url)
    text = manage_file.get_text_from_image(BROWSER, photo)
    stavka = parse_bet(text)
    match_array= parimatch_betting.search_bet(BROWSER)
    match_links = []
    for bet in stavka :
        link = ''
        flag = False
        for i in range(len(match_array)) :
            for j in range(len(match_array[i])) :
                if (match_array[i][j]['title'] == bet['match']) and not(flag) :
                    link = match_array[i][j]['link']
                    flag = True
        match_links.append(link)        
    for i in range(len(stavka)) :
        if match_links[i] == '' :
            manage_file.Error(0x2)
            continue
        if parimatch_betting.bet(BROWSER, match_links[i], stavka[i]) == 'nice' :
            print('all is done right, grats!')