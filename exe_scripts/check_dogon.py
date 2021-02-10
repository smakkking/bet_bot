import functools
import logging
import time
import copy
import sys
import json
from selenium.common.exceptions import NoSuchElementException

from global_constants import GROUP_OFFSET, BOOKMAKER_OFFSET, SERVER_DATA_PATH
import bet_manage

def check_and_delete(DATA, bk_events, data_key) :
    # возможно здесь нужно создавать браузер
    # нельзя ставку убирать из догона
    #appe = []

    for x in DATA[data_key]['coupon'].dogon :
        DATA[data_key]['coupon'].delete_id['dogon'].append(x.id)

        if not (GROUP_OFFSET[data_key].DOGON_AGGREGATOR in x.bk_links.keys()) or \
                x.bk_links[GROUP_OFFSET[data_key].DOGON_AGGREGATOR] is None:
            continue
        else:
            try:
                result = BOOKMAKER_OFFSET[GROUP_OFFSET[data_key].DOGON_AGGREGATOR].dogon_check(x)
            except NoSuchElementException:
                logging.getLogger("check_dogon").error("no element")
                result = None

        if result is None :
            x.change_id()
            continue

        if not result :
            t = copy.deepcopy(x)
            t.change_id()
            t.outcome_index[1] += 1
            # при догоне сумма увел в 2 раза
            t.summ_multiplier *= 2
            DATA[data_key]['coupon'].add_bet(t)

            for key in BOOKMAKER_OFFSET.keys():
                t.set_bk_link(key, BOOKMAKER_OFFSET[key].get_info(t, bk_events[key]))

    #for x in appe:
    #    DATA[data_key]['coupon'].add_bet(x, to_dogon=True)


def main(DATA):
    # возможно переделать на параллельное выполнение

    bk_events = {}
    for key in BOOKMAKER_OFFSET.keys():
        bet_manage.file_is_available(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json')
        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json', 'r', encoding="utf-8") as f:
            dat = json.load(f)
            bk_events[key] = dat['events']

    for key in DATA.keys():
        check_and_delete(DATA, bk_events, key)
    return DATA

if __name__ == '__main__':

    DATA = bet_manage.read_groups()
    DATA = main(DATA)
    if '-write' in sys.argv:
        bet_manage.write_groups(DATA)


