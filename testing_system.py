# здесь тестируем все модули по группам и букмекеркам

from bet_manage import LastGroupPost, YandexAPI_detection

from moduls.bookmaker_moduls import BETSCSGO_betting

import nltk, json


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


if __name__ == "__main__" :
    #testing_group(BETSPEDIA_group, 50)

    #doesnot_pass = [
    #    # новый шаблон
    #    'https://sun9-38.userapi.com/impf/2k4YRTdUlwqSwuXRfAnmoaH7cxILL9dHum-VEA/tk-8V7adqJk.jpg?size=500x423&quality=96&proxy=1&sign=7a3d67aa1372dd55246e155c707f5479&c_uniq_tag=CntqyXN_qjYEnKbDSqMbRFnWPsUDTEBLSfXr9gq4CCw',
    #    'https://sun9-43.userapi.com/impg/OvyJDiOWfBUrZiGdkktrNgY4hGXol2SZyBWfUQ/M3hTB8ic4rc.jpg?size=1080x999&quality=96&proxy=1&sign=fbb50fa50b3474b1958d44e89cb50394&c_uniq_tag=L7lBqNbnMK9jSClvt0MA5SoUZ78zi9bvgMuPpGZrFTs&type=album',
    #]
    #text = "\u270c\ud83c\udffb \u0420\u0435\u0448\u0438\u043b \u0432\u043b\u0435\u0442\u0435\u0442\u044c \u043d\u0430 \u044d\u0442\u043e\u0442 \u043c\u0430\u0442\u0447, \u043d\u0435 \u0437\u043d\u0430\u044e \u043f\u043e\u0447\u0435\u043c\u0443, \u043d\u043e \u043c\u043d\u0435 \u043a\u0430\u0436\u0435\u0442\u0441\u044f, Gambit \u0441\u043c\u043e\u0433\u0443\u0442 \u043e\u0442\u0436\u0430\u0442\u044c \u043e\u0434\u043d\u0443 \u043a\u0430\u0440\u0442\u0443 \u043a\u0430\u043a \u043c\u0438\u043d\u0438\u043c\u0443\u043c.\n\n\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u044e\u0442 \u043d\u0435\u0432\u044a\u0435\u0431\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b, \u043f\u043e\u0447\u0435\u043c\u0443 \u0431\u044b \u043d\u0435 \u0443\u0434\u0438\u0432\u0438\u0442\u044c \u0438 \u0434\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0432\u0441\u0435\u043c, \u0447\u0442\u043e \u043e\u043d\u0438 \u0447\u0442\u043e-\u0442\u043e \u043c\u043e\u0433\u0443\u0442 \u0441\u0434\u0435\u043b\u0430\u0442\u044c \u043f\u0440\u043e\u0442\u0438\u0432 \u0442\u0430\u043a\u0438\u0445 \u043a\u043e\u043c\u0430\u043d\u0434! \u0422\u0435\u043c \u0431\u043e\u043b\u0435\u0435, \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b \u0438\u0434\u0443\u0442 \u043d\u0435 \u0441\u0442\u0432\u0431\u0438\u043b\u044c\u043d\u043e + \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0432 \u0440\u043e\u0441\u0442\u0435\u0440\u0435 \u0432 \u043f\u043b\u0430\u043d\u0435 \u0440\u043e\u043b\u0435\u0439.\n\n\u2014 \u041c\u043e\u044f \u0441\u0442\u0430\u0432\u043a\u0430: \u041f\u043e\u0431\u0435\u0434\u0430 \ud83c\uddf7\ud83c\uddfa Gambit \u043d\u0430 \u043f\u0435\u0440\u0432\u043e\u0439 \u043a\u0430\u0440\u0442\u0435 25.000\u20bd, \u043f\u0440\u043e\u0438\u0433\u0440\u0430\u044e\u0442, \u0443\u0432\u0435\u043b\u0438\u0447\u0443 \u043d\u0430 \u0432\u0442\u043e\u0440\u0443\u044e! \n\n\u2014 \u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u044e \u0441\u0442\u0430\u0432\u0438\u0442\u044c: 7-10%!"

    BETSCSGO_betting.find_bet()







