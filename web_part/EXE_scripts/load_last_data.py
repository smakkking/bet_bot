from moduls import bet_manage
from manage import ALL_POSTS_JSON_PATH, CHROME_DIR_PACKAGES
from moduls.bet_manage import GROUP_OFFSET

import json
from multiprocessing import Pool
import nltk

OLD_DATA = {}

def load_last_data(group_off) :
    post = bet_manage.LastGroupPost()
    browser = bet_manage.create_webdriver()
    try :
        post.change_wall(GROUP_OFFSET[group_off].WALL_URL)
        post.get()
        if (GROUP_OFFSET[group_off].NAME in OLD_DATA.keys()) and OLD_DATA[GROUP_OFFSET[group_off].NAME]['text'] == post.text :
            post.parse_bet = False
        else :
            check_templates(browser, GROUP_OFFSET[group_off], post)
    except :
        post.parse_bet = False
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
    if post.coupon.bets == [] :
        post.parse_bet = False

def main() :
    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        OLD_DATA = json.load(last_posts_json)
    with Pool(processes=len(GROUP_OFFSET.values())) as pool :
        new_data = dict(pool.map(load_last_data, GROUP_OFFSET.keys()))
    with open(ALL_POSTS_JSON_PATH, 'w') as last_posts_json :
        json.dump(new_data, last_posts_json, indent=4)
    
if __name__ == "__main__":
    main()
    