# общие модули
import manage_file
import time
# конкретные модули

WALL_GET_url = 'https://vk.com/rushbet.tips'

def parse_bet(text) :
    # таблица смещений
    # отображение группа -> общая форма
    offset_table = {
        # победитель по карте
            'Победа. Карта' : 'map_winner',
            'Победитель. Карта' : 'map_winner',
            'Результат. Карта' : 'map_winner',
        # фора по карте 
            'Фора. Карта' : 'map_handicap',
        # тотал по карте
            'Тотал. Карта' : 'map_total',
        # победа команды
            'Результат матча' : 'match_result',
            'Победа' : 'match_result',
        # фора 
            'Фора' : 'handicap',
        # конкретный счет
            'Счет' : 'score',
        # тотал(сумма счетов)
            'Тотал' : 'total',
    }
    result = {}
    # здесь по идее иедт проверка на ставку по шаблонам
    if template1(text) or template2(text) :
        result['type'] = 'ordn'
        bet = {}
        bet['winner'] = text[0]
        for key in offset_table.keys() :
            #print(text[2].find(key))
            if text[2].find(key) != -1 :
                if offset_table[key].find('map') > 0 :
                    bet['outcome_index'] = (offset_table[key], int(text[2][-1]))
                else :
                    bet['outcome_index'] = offset_table[key]
                break
        bet['summ'] = 20.0
        bet['match_title'] = text[3][text[3].find(':') + 4 : ]
        result['bets'].append(bet)
    return result

    """
    RETURN
    {
        'type' : expr | sys | ordn
        'bets' : [
            {
                'summ' : число
                'match_title' : 'team1 - team2'
                'outcome_index' : в соответствии с таблицей смещений
                'winner' : данные о победителе
            },
            много словарей
            ....
        ]
        
    }
    """
    """ 
    c суммой ставки пока не понятно, но планирую сделать так:
    на каждый промежуток кэффов юзер сам устанавливает сумму,
    соответсвенно будем брать данные из БД    
    """

def template1(text) :
    # это если ставка ординар!!!
    if len(text) != 7 :
        return False
    if text[4] != 'Сумма пари' or text[6].find('Возможный выигрыш') == -1 :
        return False
    return True

def template2(text) :
    if len(text) != 6 :
        return False
    data_time = text[1].replace(' ', '')
    if data_time.find(':') != len(data_time) - 3 :
        return False
    return True

def main_script(BROWSER, post_before : dict, cycle_encounter : int) :
    # что происходит:
    # получается последнее фото со страницы, берется текст с фото, парсится ставка
    # сам процесс ставки
    post = manage_file.get_last_post(BROWSER, WALL_GET_url)
    if post == post_before :
        return post
    # здесь нужно понять, как отличать ставку от поста с другим содержанием(нужно изучить посты)
    stavka = []
    for photo in post['list_of_photo'] :
        obj = parse_bet(manage_file.get_text_from_image(BROWSER, photo))
        if obj != {} :
            stavka.append(obj)
    print(stavka)
    # получили массив ставок

if __name__ == "__main__":
    browser = manage_file.create_webdriver()
    try :
        main_script(
            browser, 
            { 'text' : '', 'list_of_photo' : [] },
            0
        )
    finally :
        browser.close()
        browser.quit()