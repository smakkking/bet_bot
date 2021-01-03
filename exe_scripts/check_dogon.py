import time

import functools



from global_constants import GROUP_OFFSET, BOOKMAKER_OFFSET, ALL_POSTS_JSON_PATH
import bet_manage

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
            # при догоне сумма увел в 2 раза
            x.summ_multiplier *= 2
            DATA[data_key]['coupon'].add_bet(x)
        pass
    DATA[data_key]['coupon'].dogon = new_dogon

    return (data_key, DATA[data_key])


def main(DATA, main_logger=None):

    if main_logger :
        now = time.time()

    DATA = dict(map(functools.partial(check_and_delete, DATA), DATA.keys()))

    if main_logger :
        main_logger.info('{0:.2f} spent'.format(time.time() - now))

    return DATA

if __name__ == '__main__':
    while True :
        DATA = bet_manage.read_groups()
        bet_manage.write_groups(main(DATA))

