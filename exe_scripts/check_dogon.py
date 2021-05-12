import copy
import sys
import json

from global_constants import SERVER_DATA_PATH
from global_links import GROUP_OFFSET, BOOKMAKER_OFFSET
import bet_manage


def check_and_delete(DATA, bk_events, data_key):
    has_changed = False

    for x in DATA[data_key]['coupon'].dogon:
        DATA[data_key]['coupon'].delete_id['dogon'].append(x.id)

        if not (GROUP_OFFSET[data_key].DOGON_AGGREGATOR in x.bk_links.keys()) or \
                x.bk_links[GROUP_OFFSET[data_key].DOGON_AGGREGATOR] is None:
            continue
        else:
            result = BOOKMAKER_OFFSET[GROUP_OFFSET[data_key].DOGON_AGGREGATOR].dogon_check(
                x)

        if result is None:
            x.change_id()
            continue

        has_changed = True
        if not result:
            t = copy.deepcopy(x)
            t.change_id()
            t.outcome_index[1] += 1

            t.summ_multiplier += 1
            DATA[data_key]['coupon'].add_bet(t)

            # TODO если букмекер не загружает данные о матчах в файл?
            for key in BOOKMAKER_OFFSET.keys():
                if not BOOKMAKER_OFFSET[key].TAKES_MATCHES_LIVE:
                    t.set_bk_link(
                        key, BOOKMAKER_OFFSET[key].get_info(t, bk_events[key]))

    return has_changed


def main(DATA):
    bk_events = {}
    for key in BOOKMAKER_OFFSET.keys():
        bet_manage.file_is_available(
            SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json')
        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/matches.json', 'r', encoding="utf-8") as f:
            dat = json.load(f)
            bk_events[key] = dat['events']

    change = False
    for key in DATA.keys():
        change |= check_and_delete(DATA, bk_events, key)

    return DATA if change else None


if __name__ == '__main__':

    DATA = bet_manage.read_groups()
    DATA = main(DATA)
    if '-write' in sys.argv:
        bet_manage.write_groups(DATA)
