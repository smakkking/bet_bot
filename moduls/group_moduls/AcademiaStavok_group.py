# строка для правильной работы импортирования пакетов
import sys
sys.path[0] = sys.path[0][ : sys.path[0].find('bet_bot') + 7]

from moduls import manage_file
import time

LAST_DATA = manage_file.LastGroupPost(wall_url='https://vk.com/akademiya_stavki_csgo')

def template1(text) :
    flag = True
    flag = flag and text[4] == 'vs'
    flag = flag and text[len(text) - 1] == 'ОТМЕНИТЬ СТАВКУ'
    return flag

def parse1(photo_url, text) :
    bet = {}

    bet['match_title'] = text[1].replace('vs', '-')
    bet['summ'] = 20.0

    side = define_side_winner(photo_url)
    if side == 'left' :
        bet['winner'] = text[6]
    elif side == 'right' :
        bet['winner'] = text[7]
    
    for key in offset_table.keys() :
        if text[2].find(key) != -1 :
            if offset_table[key].find('map') != -1 :
                pos = text[2].find('#')
                map_number = int(text[2][pos + 1])
                bet['outcome_index'] = (text[2][pos + 4 : ], map_number)
            else :
                bet['outcome_index'] = text[2]
    return bet


BET_TEMPLATES = [
    (template1, parse1),
]
offset_table = {
    # победитель по карте
        'ПОБЕДА НА КАРТЕ' : 'map_winner',
    # победа команды
        'ПОБЕДА В МАТЧЕ' : 'match_result',
}

# return 'left' or 'right'
def define_side_winner(url) :
    from PIL import Image
    import requests

    def otkl(color) :
        flag = True
        green = (182, 235, 52)
        for i in range(len(color)) :
            flag = flag and abs(color[i] - green[i]) < 2
        return flag

    resp = requests.get(url, stream=True).raw
    image = Image.open(resp)

    obj = image.load()
    w, h = image.size
    green_array = []
    for x in range(w) :
        for y in range(h) :
            if otkl(obj[x, y]) :
                green_array.append((x, y))

    count_left = 0
    count_right = 0          
    for (x, y) in green_array :
        if x < w / 2 :
            count_left += 1
        else :
            count_right += 1

    if count_right == len(green_array) :
        return 'right'
    elif  count_left == len(green_array) :
        return 'left'
        
    
if __name__ == "__main__":
    browser = manage_file.create_webdriver()
    try :
        pass
    finally :
        browser.close()
        browser.quit()
