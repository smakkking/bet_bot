import functools
from multiprocessing import Pool
import json
import pickle
import logging

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
                        if stavka.bk_links[client['bookmaker']] is None :
                            continue

                        result = BOOKMAKER_OFFSET[client['bookmaker']].make_bet(
                            stavka,
                            client['bet_summ'],
                            session
                        )
                        result = json.loads(result)
                        logging.getLogger("created_bets").info(client['id'])
                        logging.getLogger("created_bets").info(result['success'])
                        if not result['success']:
                            logging.getLogger("created_bets").info(result['error'])


    bet_manage.file_is_available(SERVER_DATA_PATH + bookmaker + '/sessions.json')
    with open(SERVER_DATA_PATH + bookmaker + '/sessions.json', 'r') as f :
        last_ = json.load(f)

    bet_manage.file_is_available(SERVER_DATA_PATH + bookmaker + '/sessions.json')
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

        bet_manage.file_is_available(SERVER_DATA_PATH + BOOKMAKER_OFFSET[key].NAME + '/sessions.json')
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


    return DATA


if __name__ == '__main__' :
    #while True :
    DATA = bet_manage.read_groups()
    bet_manage.write_groups(main(DATA))

    