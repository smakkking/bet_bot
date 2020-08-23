# общие модули
from moduls import manage_file
import time
# конкретные модули

WALL_GET_url = 'https://vk.com/rushbet.tips'

# сюда помещать функции-шаблоны
BET_TEMPLATES = [
    template1,
    template2,
]

# таблица смещений
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

def parse_bet(text) :
    # здесь по идее иедт проверка на ставку по шаблонам
    check = False
    for check_bet in BET_TEMPLATES :
        check = check or check_bet(text)
    if check :
        result = manage_file.Coupon('ordn')
        bet = {}

        bet['winner'] = text[0]
        bet['summ'] = 20.0
        bet['match_title'] = text[3][text[3].find(':') + 4 : ]

        for key in offset_table.keys() :
            #print(text[2].find(key))
            if text[2].find(key) != -1 :
                if offset_table[key].find('map') > 0 :
                    bet['outcome_index'] = (offset_table[key], int(text[2][-1]))
                else :
                    bet['outcome_index'] = offset_table[key]
                break
        result.add_bet(bet)
    return result

def template1(text) :
    flag = True
    flag = flag and len(text) == 7
    flag = flag and text[4] == 'Сумма пари'
    flag = flag and text[6].find('Возможный выигрыш') != -1
    return flag

def template2(text) :
    flag = True
    flag = flag and len(text) == 6
    data_time = text[1].replace(' ', '')
    flag = flag and data_time.find(':') == (len(data_time) - 3)
    return flag

def main_script(BROWSER, post_before) :
    # что происходит:
    # получается последнее фото со страницы, берется текст с фото, парсится ставка
    # сам процесс ставки
    post = manage_file.get_last_post(BROWSER, WALL_GET_url)
    if post == post_before :
        return post
    # здесь нужно понять, как отличать ставку от поста с другим содержанием(нужно изучить посты)
    stavka = []
    for photo in post.photo_list :
        obj = parse_bet(manage_file.get_text_from_image(BROWSER, photo))
        if obj != {} :
            stavka.append(obj)
    # получили массив ставок

if __name__ == "__main__":
    browser = manage_file.create_webdriver()
    try :
        main_script(
            browser, 
            manage_file.GroupPost('', []),
        )
    finally :
        browser.close()
        browser.quit()