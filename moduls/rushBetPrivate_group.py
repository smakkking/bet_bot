# общие модули
import manage_file
import parimatch_betting
import time
# конкретные модули
COUNT_POSTS = 0
WALL_GET_url = 'https://vk.com/club192973242'

def parse_bet(text) :
    #text =
    #{
    #   'победитель' - либо 'название команды', либо 'название команды(+1.5)', фора или больше меньше 
    #   'кэфф'
    #   'название ставки' - парсим его в индекс, можно составить таблицу
    #   'время и дата матча'
    #   '-'
    #   'сумма пари'
    #}
    # возможны неточности в распознавании
    BALANCE_COEFFICIENT = 1 / 100
    try : 
        if len(text) == 7 :
            str_match = text[3][text[3].find(':') + 4:]
            str_match = str_match.replace('-', '').replace(' ', '')
            return {
                'match' : str_match.upper(),
                'winner' : text[0],
                'summ' : str(float(text[5][0:(len(text[5]) - 7)]) * BALANCE_COEFFICIENT),
                'outcome_index' : text[2]
            }
        elif len(text) == 6 :
            str_match = text[2][text[2].find(':') + 4:]
            str_match = str_match.replace(' - ', '')
            return {
                'match' : str_match.upper(),
                'winner' : text[0],
                'summ' : str(float(text[5][0:(len(text[4]) - 7)]) * BALANCE_COEFFICIENT),
                'outcome_index' : text[2][0:text[2].find(':') - 10]
            }
    except :
        return {
                'match' : 'error',
                'winner' : 'error',
                'summ' : 'error',
                'outcome_index' : 'error'
            }

def main_script(BROWSER) :
    # что происходит:
    # получается последнее фото со страницы, берется текст с фото, парсится ставка
    # идет поиск всех матчей по совпадению со ставкой  
    # сам процесс ставки
    photo = get_last_photo(BROWSER)
    text = manage_file.get_text_from_image(BROWSER, photo)
    if text == [] or (len(text) != 6 and len(text) != 7) :
        manage_file.Error(0x1)
        return photo
    stavka = parse_bet(text)
    if stavka['match'] == 'error' and stavka['winner'] == 'error' :
        manage_file.Error(0x1)
        return photo
    print(stavka)
    match_array = parimatch_betting.search_bet(BROWSER)
    match_link = ''
    flag = False
    for i in range(3) :
        for j in range(len(match_array[i])) :
            if match_array[i][j]['title'] == stavka['match'] and not(flag) :
                match_link = match_array[i][j]['link']
                flag = True
    if match_link == '' :
        manage_file.Error(0x2)
        return photo
    if parimatch_betting.bet(BROWSER, match_link, stavka) == 'nice' :
        print('all is done right, grats!')
    return photo

def get_last_photo(BROWSER) :
    manage_file.get_html_with_browser(BROWSER, WALL_GET_url, manage_file.WAIT_TIME)
    items = BROWSER.find_elements_by_xpath("//a[@class='page_post_thumb_wrap image_cover  page_post_thumb_last_column page_post_thumb_last_row']")
    items[COUNT_POSTS].click()
    time.sleep(3)
    return BROWSER.find_element_by_id('pv_photo').find_element_by_tag_name('img').get_attribute('src')

    