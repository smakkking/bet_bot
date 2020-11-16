from moduls import bet_manage
from manage import ALL_POSTS_JSON_PATH, CHROME_DIR_PACKAGES
from moduls.bet_manage import GROUP_OFFSET

import json
from multiprocessing import Pool
import nltk

OLD_DATA = {}

def load_last_data(group_off) :
    # загружает данные с группы
    browser = bet_manage.create_webdriver()
    # изменить бит уникальности в зависимости от old_data
    post = bet_manage.LastGroupPost()
    post.get(browser, GROUP_OFFSET[group_off].WALL_URL)

    if (GROUP_OFFSET[group_off].NAME in OLD_DATA.keys() and OLD_DATA[GROUP_OFFSET[group_off].NAME]['text'] == post.text) :
        post.parse_bet = False
    else :
        check_templates(browser, GROUP_OFFSET[group_off], post)

    browser.close()
    browser.quit()
    return (GROUP_OFFSET[group_off].NAME, post.__json_repr__())

def check_templates(BROWSER, group_module, post) :
        for photo in post.photo_list :
            text = bet_manage.get_text_from_image(BROWSER, photo)
            text = ' '.join(text)
            for (tmp, parse) in group_module.BET_TEMPLATES :
                if (tmp(text)) :
                    post.coupon.add_bet(parse(photo, nltk.word_tokenize(text)))
        if not post.coupon.bets :
            post.parse_bet = False

def main() :
    with Pool(processes=len(GROUP_OFFSET.values())) as pool :
        with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
            OLD_DATA = json.load(last_posts_json)
        new_data = dict(pool.map(load_last_data, GROUP_OFFSET.keys()))
        with open(ALL_POSTS_JSON_PATH, 'w') as last_posts_json :
            json.dump(new_data, last_posts_json, indent=4)
    