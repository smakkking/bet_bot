import time
import json
import jsonpickle
import pickle

from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH
from exe_scripts import scan_database

def main() :

    data = scan_database.main()

    for v in BOOKMAKER_OFFSET.keys() :
        if BOOKMAKER_OFFSET[v].HAS_API :
            continue

        session_array = []
        for client in data :
            if client['bookmaker'] == v :
                sess_info = BOOKMAKER_OFFSET[client['bookmaker']].create_session(
                    client['bookmaker_login'],
                    client['bookmaker_password']
                )
                with open(SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client['id']), 'wb') as f:
                    pickle.dump(sess_info['session'], f)
                    sess_info['session'] = SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client['id'])
                session_array.append(sess_info)

        with open(SERVER_DATA_PATH + 'betscsgo/sessions.json', 'w') as f:
            json.dump(session_array, f, indent=4)
    #query = 'https://betscsgo.in/index/placebet/266831/2/1/' + sess_info['betscsgo_token']
    #r = sess_info['session'].get(query)
    #print(r.text)

if __name__ == '__main__' :
    main()
