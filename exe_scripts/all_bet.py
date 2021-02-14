import functools
from multiprocessing import Pool
import json
import pickle
import logging
import copy


from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH
import bet_manage
from exe_scripts import scan_database

def bbet_client(DATA, sessions, client):
    if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API:
        # ставить по api возможности пока нет
        pass
    else:
        try:
            session = sessions[str(client['id'])]
        except KeyError:
            return
        for group in client['groups']:
            if DATA[group]['parse_bet']:
                for stavka in DATA[group]['coupon'].bets:
                    if not (client['bookmaker'] in stavka.bk_links.keys()):
                        continue
                    if stavka.bk_links[client['bookmaker']] is None:
                        continue

                    result = BOOKMAKER_OFFSET[client['bookmaker']].make_bet(
                        stavka,
                        client['bet_summ'],
                        session
                    )
                    try:
                        result = json.loads(result)
                    except json.decoder.JSONDecodeError:
                        result = {
                            'success': False,
                            'error': "unknown"
                        }
                    logging.getLogger("created_bets").info(client['id'])
                    logging.getLogger("created_bets").info(result['success'])
                    if not result['success']:
                        logging.getLogger("created_bets").error(result['error'])

def bbet_all(DATA, bkm) :

    # новая готовящаяся версия лежит в папке bet_bot

    bookmaker = bkm['clients'][0]['bookmaker']

    #with Pool(processes=len(bkm['clients'])) as p:
    #    p.map(functools.partial(bbet_client, DATA, bkm['sessions']), bkm['clients'])

    for client in bkm['clients'] :
        if BOOKMAKER_OFFSET[client['bookmaker']].HAS_API :
            # ставить по api возможности пока нет
            pass
        else :
            try:
                session = bkm['sessions'][str(client['id'])]
            except KeyError:
                continue
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
                        try:
                            result = json.loads(result)
                        except json.decoder.JSONDecodeError:
                            result = {
                                'success' : False,
                                'error' : "unknown"
                            }
                        logging.getLogger("created_bets").info(client['id'])
                        logging.getLogger("created_bets").info(result['success'])
                        if not result['success']:
                            logging.getLogger("created_bets").info(result['error'])

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

    bbet_all(DATA, bkm['betscsgo'])


    # КАК ПРОИСХОДИТ ПЕРЕВОД В ДОГОН?
    for group in DATA.keys() :
        for x in DATA[group]['coupon'].bets :
            if x.dogon and x.outcome_index[1] < 4 :
                t = copy.deepcopy(x)
                t.change_id()
                DATA[group]['coupon'].add_bet(t, to_dogon=True)
            DATA[group]['coupon'].delete_id['bets'].append(x.id)


    return DATA


if __name__ == '__main__' :
    #while True :
    DATA = bet_manage.read_groups()
    bet_manage.write_groups(main(DATA))

    