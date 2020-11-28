# здесь тестируем все модули по группам и букмекеркам

import manage
from moduls.bet_manage import Stavka, LastGroupPost, YandexAPI_detection

from moduls.group_moduls import BETSPEDIA_group
from moduls.bookmaker_moduls import BETSCSGO_betting

from manage import ALL_POSTS_JSON_PATH
import nltk, time, json


def testing_group(group, N) :
    p = LastGroupPost(group.WALL_URL)
    YandexAPI_detection.create_new_token(debug=True)
    
    if N // 100 == 0 :
        p.get(0, N)
    else :
        for offset in range(N // 100) :
            p.get(100 * offset, 100)
        if N % 100 != 0 :
            p.get((N // 100) * 100, N % 100)
         

    bbb = []

    for photo in p.photo_list :
        #print(photo)
        try :
            a = YandexAPI_detection(photo)
            text = a.text_detection()
            text_nltk = nltk.word_tokenize(text)
            text = text.upper()

            stavka = None

            for (tmp, parse) in group.BET_TEMPLATES :
                if tmp(text) :
                    stavka = parse(photo, text_nltk)
        except Exception as e :
            bbb.append({
                'link' : photo,
                'text' : '',
                'stavka' : f'failed because of: {e}'
            })
        else :
            if stavka is None :
                bbb.append({
                    'link' : photo,
                    'text' : text,
                    'stavka' : 'not_bet'
                })
            else :
                bbb.append({
                    'link' : photo,
                    'text' : text,
                    'stavka' : stavka.__json_repr__(),
                })

    with open(r'C:\GitRep\bet_bot\web_part\user_data\test.json', 'w') as f :
        json.dump(bbb, f, indent=4)

def get_stavka(photo_url, group) :
    YandexAPI_detection.create_new_token(debug=True)
    a = YandexAPI_detection(photo_url)
    text = a.text_detection()
    text_nltk = nltk.word_tokenize(text)
    text = text.upper()
    

    stavka = None

    for (tmp, parse) in group.BET_TEMPLATES :
        if tmp(text) :
            stavka = parse(photo_url, text_nltk)
    if stavka is None :
        return None
    else :
        return stavka.__json_repr__()

def llogin(bookmaker) :
    class u() :
        def __init__(self, a, b, c) :
            self.chrome_dir_path = a
            self.bookmaker_login = b
            self.bookmaker_password = c

    a = u('16065607583527613', 'Karkadav', ';:9N8;,Emg@LkQ[')

    bookmaker.login(a)


if __name__ == "__main__" :
    #testing_group(BETSPEDIA_group, 50)

    doesnot_pass = [
        # новый шаблон
        'https://sun9-38.userapi.com/impf/2k4YRTdUlwqSwuXRfAnmoaH7cxILL9dHum-VEA/tk-8V7adqJk.jpg?size=500x423&quality=96&proxy=1&sign=7a3d67aa1372dd55246e155c707f5479&c_uniq_tag=CntqyXN_qjYEnKbDSqMbRFnWPsUDTEBLSfXr9gq4CCw',
    ]

    llogin(BETSCSGO_betting)





