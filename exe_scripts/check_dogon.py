import functools

from global_constants import GROUP_OFFSET, BOOKMAKER_OFFSET


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


def main(DATA):
    DATA = dict(map(functools.partial(check_and_delete, DATA), DATA.keys()))

    return DATA


