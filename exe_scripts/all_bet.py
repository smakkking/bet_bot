import functools
import time
from multiprocessing import Pool

from global_constants import BOOKMAKER_OFFSET

def bbet_all(DATA, client) :
    k = 0
    if not BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
        browser = BOOKMAKER_OFFSET[client['bookmaker']].init_config(client['chrome_dir_path'])
        for group in client['groups']:
            if DATA[group]['parse_bet']:
                for stavka in DATA[group]['coupon'].bets:
                    result = BOOKMAKER_OFFSET[client['bookmaker']].make_bet(
                        browser,
                        stavka,
                        summ=client['bet_summ'],
                        first_time=(k == 0)
                    )
                    k += 1

        browser.close()
        browser.quit()
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
        main_logger.info('{0:.2f} spent on bet process'.format(time.time() - now))

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

    
    