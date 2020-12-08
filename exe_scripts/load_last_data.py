import json
import nltk
import functools
import time
import logging
from logging import config
from multiprocessing import Pool

import bet_manage
from global_constants import ALL_POSTS_JSON_PATH, GROUP_OFFSET, BET_PROJECT_ROOT
from bet_manage import YandexAPI_detection


def load_last_data(OLD_DATA, token, group_off) :
    post = bet_manage.LastGroupPost(GROUP_OFFSET[group_off].WALL_URL)
    try :
        post.get()
        if (group_off in OLD_DATA.keys()) and OLD_DATA[group_off]['text'] == post.text :
            post.parse_bet = False
        else :
            GROUP_OFFSET[group_off].check_templates(post, token)
    except Exception as e:
        post.parse_bet = False
        logger = logging.getLogger(GROUP_OFFSET[group_off].NAME)
        logger.error(f'loading failed because of {e}')
    return (group_off, post.__json_repr__())


def main(main_logger=None) :
    # create logger

    dictLogConfig = {
        "version":1,
        "handlers":{
            "fileHandler":{
                "class":"logging.FileHandler",
                "formatter":"myFormatter",
                "filename": BET_PROJECT_ROOT + "moduls/group_moduls/groups.log",
            }
        },
        "loggers":{},
        "formatters":{
            "myFormatter":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }

    for k in GROUP_OFFSET.keys() :
        dictLogConfig['loggers'][k] = {
            "handlers": ["fileHandler"],
            "level": "INFO",
        }

    #config.dictConfig(dictLogConfig)

    if main_logger :
        now = time.time()

    YandexAPI_detection.create_new_token()

    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        OLD_DATA = json.load(last_posts_json)

    with Pool(processes=len(GROUP_OFFSET.values())) as pool :
        new_data = dict(pool.map(functools.partial(load_last_data, OLD_DATA, YandexAPI_detection.iam_token), GROUP_OFFSET.keys()))

    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(new_data, last_posts_json, indent=4)

    if main_logger :
        main_logger.info('{0:.2f} spent on load data from group'.format(time.time() - now))


if __name__ == "__main__":
    main()
    