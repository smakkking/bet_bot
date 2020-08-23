from moduls import manage_file
import time

BET_TEMPLATES = [
    template1,
]

offset_table = {
    # победитель по карте
        'ПОБЕДА НА КАРТЕ' : 'map_winner',
    # победа команды
        'ПОБЕДА В МАТЧЕ' : 'match_result',
}

def parse_bet(photo_url, text) :
    for check_bet in BET_TEMPLATES :
        check = check or check_bet(text)

    if check :
        result = manage_file.Coupon('ordn')
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
        result.add_bet(bet)
        return result
    else :
        return None 

def template1(text) :
    flag = True
    flag = flag and text[4] == 'vs'
    flag = flag and text[len(text) - 1] == 'ОТМЕНИТЬ СТАВКУ'
    return flag

    
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
        