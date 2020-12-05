from moduls import bet_manage
from manage import ALL_POSTS_JSON_PATH, CHROME_DIR_PACKAGES
from moduls.bet_manage import GROUP_OFFSET
from moduls.bet_manage import YandexAPI_detection

import json, nltk, functools
from multiprocessing import Pool

def load_last_data(OLD_DATA, token, group_off) :
    post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try :
        post.get()
        if (group_off in OLD_DATA.keys()) and OLD_DATA[group_off]['text'] == post.text :
            post.parse_bet = False
        else :
            #check_templates(GROUP_OFFSET[group_off], post, token)
            # TODO у каждой группы есть функция check_templates(...) работает аналогично ^ но т срабатывает exception: circular import
            GROUP_OFFSET[group_off].check_templates(post, token)
    except:
        post.parse_bet = False
    return (group_off, post.__json_repr__())

def check_templates(group_module, post, token) :
    for photo_url in post.photo_list :
        obj = YandexAPI_detection(photo_url, token)
        text = obj.text_detection()
        print(text)
        for (tmp, parse) in group_module.BET_TEMPLATES :
            if tmp(text.upper()) :
                st = parse(photo_url, nltk.word_tokenize(text))
                post.coupon.add_bet(st)
    if post.find_dogon():
        post.dogon = True
    if post.coupon.bets == [] :
        post.parse_bet = False

def main() :
    # проблемы с кодировкой
    YandexAPI_detection.create_new_token()

    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        OLD_DATA = json.load(last_posts_json)

    with Pool(processes=len(GROUP_OFFSET.values())) as pool :
        new_data = dict(pool.map(functools.partial(load_last_data, OLD_DATA, YandexAPI_detection.iam_token), GROUP_OFFSET.keys()))

    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(new_data, last_posts_json, indent=4)
    
if __name__ == "__main__":
    main()
    