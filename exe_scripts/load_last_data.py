import json
import nltk
import functools
import time
from multiprocessing import Pool

import bet_manage
from global_constants import ALL_POSTS_JSON_PATH, GROUP_OFFSET
from bet_manage import YandexAPI_detection


def load_last_data(OLD_DATA, token, group_off) :
    post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try :
        post.get()
        if (group_off in OLD_DATA.keys()) and OLD_DATA[group_off]['text'] == post.text :
            post.parse_bet = False
        else :
            GROUP_OFFSET[group_off].check_templates(post, token)
    except:
        post.parse_bet = False
    return (group_off, post.__json_repr__())


def check_templates(group_module, post, token) :
    for photo_url in post.photo_list :
        obj = YandexAPI_detection(photo_url, token)
        text = obj.text_detection()
        for (tmp, parse) in group_module.BET_TEMPLATES :
            if tmp(text.upper()) :
                st = parse(photo_url, nltk.word_tokenize(text))
                post.coupon.add_bet(st)
    if post.find_dogon():
        post.dogon = True
    if post.coupon.bets == [] :
        post.parse_bet = False


def main(debug=False) :
    # TODO проблемы с кодировкой
    if debug :
        now = time.time()

    YandexAPI_detection.create_new_token()

    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        OLD_DATA = json.load(last_posts_json)

    with Pool(processes=len(GROUP_OFFSET.values())) as pool :
        new_data = dict(pool.map(functools.partial(load_last_data, OLD_DATA, YandexAPI_detection.iam_token), GROUP_OFFSET.keys()))

    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(new_data, last_posts_json, indent=4)

    if debug :
        print('{0:.2f} spent on load data from group'.format(time.time() - now))

if __name__ == "__main__":
    main()
    