import functools
from multiprocessing import Pool
import logging

from global_constants import BOOKMAKER_OFFSET
import bet_manage
from exe_scripts import scan_database


def bbet_all(DATA, clients) :
    for client in clients :
        if not BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
            session = BOOKMAKER_OFFSET[client['bookmaker']].create_session(
                client_login=client['bookmaker_login'],
                client_passwd=client['bookmaker_password']
            )

            for group in client['groups'] :
                if DATA[group]['parse_bet'] :
                    for stavka in DATA[group]['coupon'].bets :
                        if not (client['bookmaker'] in stavka.bk_links.keys()) :
                            continue
                        result = BOOKMAKER_OFFSET[client['bookmaker']].make_bet(
                            stavka,
                            client['bet_summ'],
                            session
                        )
                        print(result, client['id'])
                        logging.getLogger("all_bet").info("Client" + str(client['id']) + " gained bet:  " + result)
            session['session'].close()
        else :
            # ставить по api возможности пока нет
            pass


def main(DATA : dict, clients_DATA : dict=None, main_logger=None) :
    clients_DATA = scan_database.main()

    clients_by_bkm = {}

    for key in BOOKMAKER_OFFSET.keys() :
        clients_by_bkm[key] = []

    for client in clients_DATA :
        clients_by_bkm[client['bookmaker']].append(client)

    with Pool(processes=len(clients_by_bkm.keys())) as pool:
        pool.map(functools.partial(bbet_all, DATA), clients_by_bkm.values())


    # КАК ПРОИСХОДИТ ПЕРЕВОД В ДОГОН?
    for group in DATA.keys() :
        for x in DATA[group]['coupon'].bets :
            # не совсем четсное решение(так как карта может быть и 4-ая)
            if x.dogon and x.outcome_index[1] <= 4 :
                DATA[group]['coupon'].add_bet(x, to_dogon=True)

    # очистка coupon.bets у всех групп
    for x in DATA.keys() :
        DATA[x]['coupon'].bets = []
    return DATA


if __name__ == '__main__' :
    #while True :
    DATA = bet_manage.read_groups()
    bet_manage.write_groups(main(DATA))

    