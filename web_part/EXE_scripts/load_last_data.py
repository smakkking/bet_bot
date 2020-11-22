from moduls import bet_manage
from manage import ALL_POSTS_JSON_PATH, CHROME_DIR_PACKAGES
from moduls.bet_manage import GROUP_OFFSET
from moduls.bet_manage import YandexAPI_detection

import json, nltk, time
from multiprocessing import Pool

OLD_DATA = {}

def load_last_data(group_off, OLD_DATA) :
    # где создавать токен?
    post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try :
        post.get()
        if (group_off in OLD_DATA.keys()) and OLD_DATA[group_off]['text'] == post.text :
            post.parse_bet = False
        else :
            check_templates(GROUP_OFFSET[group_off], post)
    except Exception as e:
        post.parse_bet = False
    return (group_off, post.__json_repr__())

def check_templates(group_module, post) :
    for photo_url in post.photo_list :
        obj = YandexAPI_detection(photo_url)
        text = obj.text_detection()
        for (tmp, parse) in group_module.BET_TEMPLATES :
            if (tmp(text.upper())) :
                post.coupon.add_bet(parse(photo_url, nltk.word_tokenize(text)))
    if post.coupon.bets == [] :
        post.parse_bet = False

def main() :
    YandexAPI_detection.create_new_token()

    with open(ALL_POSTS_JSON_PATH, 'r') as last_posts_json :
        OLD_DATA = json.load(last_posts_json)
    # паралельно работать не хочет

    new_data = []
    for g in GROUP_OFFSET.keys() : 
        new_data.append(load_last_data(g, OLD_DATA))
    new_data = dict(new_data)

    #with Pool(processes=len(GROUP_OFFSET.values())) as pool :
    #    new_data = dict(pool.map(load_last_data, GROUP_OFFSET.keys()))

    with open(ALL_POSTS_JSON_PATH, 'w') as last_posts_json :
        json.dump(new_data, last_posts_json, indent=4)
    
if __name__ == "__main__":
    main()
    