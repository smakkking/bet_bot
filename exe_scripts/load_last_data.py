import functools
import logging
from multiprocessing import Pool
import json

import bet_manage
from global_constants import ALL_POSTS_JSON_PATH, GROUP_OFFSET
from bet_manage import YandexAPI_detection
from exe_scripts import find_all_links


def load_last_data(OLD_DATA, token, group_off) :
    # OLD_DATA - словари, содержащие экземпляры coupon
    post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try:
        post.get()
        if not (group_off in OLD_DATA.keys() and OLD_DATA[group_off]['text'] == post.text):
            GROUP_OFFSET[group_off].check_templates(post, token)
    except Exception as e:
        logging.getLogger("load_last_data").error(group_off + " was failed because of " + str(e))

    return (group_off, post.__dict__())


def main(queue=None) :
    YandexAPI_detection.create_new_token()

    if queue:
        queue.put(1, block=True)
    # если по каким-то неведомым причинам произошла потеря данных и в файл записалось пустота, что он должен его обновить
    try:
        with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
            DATA = json.load(last_posts_json)
    except json.decoder.JSONDecodeError:
        DATA = {}
    if queue:
        queue.get()

    with Pool(processes=len(GROUP_OFFSET.keys())) as pool :
        DATA = dict(pool.map(functools.partial(load_last_data, DATA, YandexAPI_detection.iam_token), GROUP_OFFSET.keys()))

    # DATA - словари, содержащие экземпляры coupon

    return DATA


if __name__ == "__main__":
    t = main()
    DATA = find_all_links.main(t)

    bet_manage.write_groups(DATA)
    
