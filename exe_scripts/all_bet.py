import copy
import time

from global_links import GROUP_OFFSET, BOOKMAKER_OFFSET
import bet_manage
from exe_scripts import scan_database


def main(DATA: dict):

    # проверка на то, нужно ли исполнять
    need_to_execute = False
    for val in DATA.values():
        need_to_execute |= val['parse_bet']
    if not need_to_execute:
        time.sleep(5)
        return None

    # TODO collect bk info locally in _betting.py modules functions
    bkm = {}
    for key in BOOKMAKER_OFFSET.keys():
        bkm[key] = []

    clients_DATA = scan_database.main(mode='all_bet')
    for client in clients_DATA:
        bkm[client['bookmaker']].append(client)

    # deleting duplicates(and bets, that already were)
    for group in DATA.keys():
        new_bets = []
        for x in DATA[group]['coupon'].bets:
            if x not in DATA[group]['coupon'].delay:
                new_bets.append(x)
            else:
                DATA[group]['coupon'].delete_id['bets'].append(x.id)
        DATA[group]['coupon'].bets = new_bets
        DATA[group]['bank'] = GROUP_OFFSET[group].BANK

    # TODO parallel process
    x = {}
    BOOKMAKER_OFFSET['betscsgo'].mass_bet(DATA, bkm['betscsgo'], x)

    # списание средств со счетов
    scan_database.main(mode='all_bet', payment=x['betscsgo'])

    # transfering to dogon
    for group in DATA.keys():
        for x in DATA[group]['coupon'].bets:
            if x.dogon and x.outcome_index[1] < 4 and x.bk_links[GROUP_OFFSET[group].DOGON_AGGREGATOR]:
                t = copy.deepcopy(x)
                t.change_id()
                DATA[group]['coupon'].add_bet(t, to_dogon=True)
            DATA[group]['coupon'].delete_id['bets'].append(x.id)
            DATA[group]['coupon'].add_bet(x, to_delay=True)

    return DATA


if __name__ == '__main__':
    DATA = bet_manage.read_groups()
    bet_manage.write_groups(main(DATA))
