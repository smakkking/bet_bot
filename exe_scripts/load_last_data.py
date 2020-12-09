import json
import functools
import time
from multiprocessing import Pool

import bet_manage
from global_constants import ALL_POSTS_JSON_PATH, GROUP_OFFSET, BET_PROJECT_ROOT
from bet_manage import YandexAPI_detection


# TODO need test
def load_last_data(OLD_DATA, token, group_off) :
    # OLD_DATA - словари, содержащие экземпляры coupon
    if group_off in OLD_DATA.keys() :
        post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL, old=OLD_DATA[group_off]['coupon'])
    else :
        post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try :
        post.get()
        if not (group_off in OLD_DATA.keys() and OLD_DATA[group_off]['text'] == post.text):
            GROUP_OFFSET[group_off].check_templates(post, token)
    except Exception as e:
        pass
    if post.coupon.bets == []:
        post.parse_bet = False
    return (group_off, post.__dict__())


def main(DATA, main_logger=None) :

    if main_logger :
        now = time.time()

    YandexAPI_detection.create_new_token()

    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(load_last_data, DATA, YandexAPI_detection.iam_token), GROUP_OFFSET.keys()))

    # DATA - словари, содержащие экземпляры coupon

    if main_logger :
        main_logger.info('{0:.2f} spent on load data from group'.format(time.time() - now))

    return DATA


if __name__ == "__main__":
    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        OLD_DATA = json.load(last_posts_json)
    t = main(OLD_DATA)
    # записываем обратно для более удобного восприятия
    for x in t.keys() :
        t[x]['coupon'] = t[x]['coupon'].__json_repr__()
    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(t, last_posts_json, indent=4)
    