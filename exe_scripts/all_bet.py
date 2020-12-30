import functools
import time
from multiprocessing import Pool
import logging

from global_constants import BOOKMAKER_OFFSET

def bbet_all(DATA, client) :
    k = 0
    if not BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
        # здесь происходит авторизация
        for group in client['groups'] :
            if DATA[group]['parse_bet'] :
                for stavka in DATA[group]['coupon'].bets :
                    if not (client['bookmaker'] in stavka.bk_links.keys()) :
                        continue
                    result = BOOKMAKER_OFFSET[client['bookmaker']].make_bet(
                        stavka,
                        summ=client['bet_summ']
                    )
                    print(result)
        # TODO избавиться от дубликатов, всю сумму прибавить к одной, от конкурирующих ставок хз как избавиться
        # а вот что делать, если эта ставка уже поставлена?? как поменять сумму
        # в ответ на запрос приходит словарь с ключом success - успех ставки
        # если написано сумма ставки не изменилась, то удвоить сумму

    else :
        # ставить по api возможности пока нет
        pass


def main(DATA : dict, clients_DATA : dict, main_logger=None) :

    if main_logger :
        now = time.time()

    # здесь :
    # для каждого клиента происходит процесс ставки
    # ставки из dogon в bets переносятся в другом скрипте
    # но только после скрипта find_all_links
    if clients_DATA != [] :
        with Pool(processes=len(clients_DATA)) as pool :
            bet_data = list(pool.map(functools.partial(bbet_all, DATA), clients_DATA))

    if main_logger :
        main_logger.info('{0:.2f} spent'.format(time.time() - now))

    # КАК ПРОИСХОДИТ ПЕРЕВОД В ДОГОН?
    for group in DATA.keys() :
        for x in DATA[group]['coupon'].bets :
            # не совсем четсное решение(так как карта может быть и 4-ая)
            if x.dogon and x.outcome_index[1] <= 3 :
                DATA[group]['coupon'].add_bet(x, to_dogon=True)

    # очистка coupon.bets у всех групп
    for x in DATA.keys() :
        DATA[x]['coupon'].bets = []
    return DATA

    
    