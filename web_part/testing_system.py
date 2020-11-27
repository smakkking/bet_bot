# здесь тестируем все модули по группам и букмекеркам

import manage
from moduls.bet_manage import Stavka, LastGroupPost, YandexAPI_detection


from moduls.bookmaker_moduls.BETSCSGO_betting import find_bet
from manage import ALL_POSTS_JSON_PATH
import nltk, time, json


def testing_group(group) :
    p = LastGroupPost(group.WALL_URL)
    YandexAPI_detection.create_new_token()
    # нужно получить N постов
    N = 100

    for offset in range(N // 100) :
        p.get(100 * offset, 100)

    bbb = []

    for photo in p.photo_list :
        a = YandexAPI_detection(photo)
        text = a.text_detection(debug=True).upper()
        text_nltk = nltk.word_tokenize(text)
        for (tmp, parse) in group.BET_TEMPLATES :
            if tmp(text) :
                stavka = parse(photo, text_nltk)
        
        if stavka is None :
             bbb.append({
                'link' : photo,
                'stavka' : 'not_bet'
            })
        else :
            bbb.append({
                'link' : photo,
                'stavka' : stavka.__json_repr__(),
            })

    with open(r'C:\GitRep\bet_bot\web_part\user_data\test.json', 'w') as f :
        json.dump(bbb, f, indent=4)
    
 
if __name__ == "__main__" :
    





