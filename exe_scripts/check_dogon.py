import time
from multiprocessing import Pool
import functools
import json


from global_constants import GROUP_OFFSET, BOOKMAKER_OFFSET, ALL_POSTS_JSON_PATH
from exe_scripts import load_last_data

def check_and_delete(DATA, data_key) :
    # возможно здесь нужно создавать браузер
    new_dogon = []
    for x in DATA[data_key]['coupon'].dogon :
        # какая-то функция от ставки, возв True False или None
        if not (GROUP_OFFSET[data_key].DOGON_AGGREGATOR in x.bk_links.keys()) :
            continue
        result = BOOKMAKER_OFFSET[GROUP_OFFSET[data_key].DOGON_AGGREGATOR].dogon_check(x)
        if result is None :
            new_dogon.append(x)
            continue
        if not result :
            x.outcome_index[1] += 1
            DATA[data_key]['coupon'].add_bet(x)
        pass
    DATA[data_key]['coupon'].dogon = new_dogon

    return (data_key, DATA[data_key])
    # возвращать ли кортеж ключ-значение? изменится ли DATA в main?


def main(DATA, main_logger=None):

    if main_logger :
        now = time.time()

    # не будет работать на большом числе групп
    with Pool(processes=len(DATA.keys())) as pool:
        DATA = dict(pool.map(functools.partial(check_and_delete, DATA), DATA.keys()))

    if main_logger :
        main_logger.info('{0:.2f} spent'.format(time.time() - now))

    return DATA

if __name__ == '__main__':
    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json :
        GROUP_DATA = json.load(last_posts_json)

    GROUP_DATA = load_last_data.main()

    GROUP_DATA = main(GROUP_DATA)

    for x in GROUP_DATA.keys() :
        GROUP_DATA[x]['coupon'] = GROUP_DATA[x]['coupon'].__json_repr__()
    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(GROUP_DATA, last_posts_json, indent=4)

