# общие модули
import manage_file
import parimatch_betting
import time
# конкретные модули
WALL_GET_url = 'https://vk.com/rushbet.tips'

def parse_bet(text) :
    """
    text =
    {
       'победитель' - либо 'название команды', либо 'название команды(+-1.5)', фора или больше меньше 
       'кэфф'
       'название ставки'
       'время и дата матча'
       '-'
       'сумма пари'
    }
     возможны неточности в распознавании, их желательно бы устранить
     Как работает: подается текст одной фотки, задача - определить, ординар, экспресс или система
     Если ординар - вернуть:
     {
         'expr' : False
         'ord' : True
         'sys' False
         'bet' : {здесь будет инфа о ставке(как устроена пока не понятно)}
     }
     Если экспресс - вернуть:
     {
         'expr' : True
         'ord' : False
         'sys' False
         'bet' : [массив записей о ставках]
     }
     С системой пока не ясно
    """
    BALANCE_COEFFICIENT = 1 / 100
    """ 
    c суммой ставки пока не понятно, но планирую сделать так:
    на каждый промежуток кэффов юзер сам устанавливает сумму,
    соответсвенно будем брать данные из БД    
    """

    try : 
        if len(text) == 7 :
            str_match = text[3][text[3].find(':') + 4:]
            str_match = str_match.replace('-', '').replace(' ', '')
            return {
                'match' : str_match.upper(),
                'winner' : text[0],
                'summ' : str(float(text[5][0:(len(text[5]) - 7)]) * BALANCE_COEFFICIENT),
                'outcome_index' : text[2],
            }
        elif len(text) == 6 :
            str_match = text[2][text[2].find(':') + 4:]
            str_match = str_match.replace(' - ', '')
            return {
                'match' : str_match.upper(),
                'winner' : text[0],
                'summ' : str(float(text[5][0:(len(text[4]) - 7)]) * BALANCE_COEFFICIENT),
                'outcome_index' : text[2][0:text[2].find(':') - 10],
            }
    except :
        return {}

def main_script(BROWSER, post_before : dict, cycle_encounter : int) :
    # что происходит:
    # получается последнее фото со страницы, берется текст с фото, парсится ставка
    # сам процесс ставки
    post = manage_file.get_last_post(BROWSER, WALL_GET_url)
    if cycle_encounter % 100 == 1 :
        manage_file.renew(BROWSER, 'https://new.parimatch.ru')
    if post == post_before :
        return post
    # здесь нужно понять, как отличать ставку от поста с другим содержанием(нужно изучить посты)
    stavka = []
    for photo in post['list_of_photo'] :
        obj = parse_bet(manage_file.get_text_from_image(BROWSER, photo))
        if obj != {} :
            stavka.append(obj)
    # получили массив ставок

if __name__ == "__main__":
    pass