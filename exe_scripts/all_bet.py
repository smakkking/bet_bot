import functools
from multiprocessing import Pool
import logging
import json
import pickle

from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH
import bet_manage
from exe_scripts import scan_database


def bbet_all(DATA, bkm) :
    for client in bkm['clients'] :

        bookmaker = client['bookmaker']

        if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
            # ставить по api возможности пока нет
            pass
        else :
            session = bkm['sessions'][str(client['id'])]
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

    with open(SERVER_DATA_PATH + bookmaker + '/sessions.json', 'r') as f :
        last_ = json.load(f)
    with open(SERVER_DATA_PATH + bookmaker + '/sessions.json', 'w') as f :
        for key in last_.keys() :
            bkm['sessions'][key]['session'] = last_[key]['session']
        json.dump(bkm['sessions'], f, indent=4)

def main(DATA : dict) :

    bkm = {}
    for key in BOOKMAKER_OFFSET.keys():
        bkm[key] = {}
        bkm[key]['clients'] = []
        if BOOKMAKER_OFFSET[key].HAS_API :
            continue
        #  получаем список всех активных сессий
        with open(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/sessions.json', 'r') as f :
            sessions = json.load(f)

        for sess in sessions.values() :
            with open(sess['session'], 'rb') as f :
                sess['session'] = pickle.load(f)
        bkm[key]['sessions'] = sessions

    clients_DATA = scan_database.main()
    for client in clients_DATA :
        bkm[client['bookmaker']]['clients'].append(client)


    with Pool(processes=len(bkm.values())) as pool:
        pool.map(functools.partial(bbet_all, DATA), bkm.values())


    # КАК ПРОИСХОДИТ ПЕРЕВОД В ДОГОН?
    for group in DATA.keys() :
        for x in DATA[group]['coupon'].bets :
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

    