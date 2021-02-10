import json
import pickle
import shutil
import os

from global_constants import BOOKMAKER_OFFSET, SERVER_DATA_PATH
from bet_manage import SQL_DB


def main() :
    a = SQL_DB()
    data = a.SQL_SELECT(
        ['bookmaker', 'id', 'bookmaker_login', 'bookmaker_password'],
        where_cond='sub_status=1'
    )

    for v in BOOKMAKER_OFFSET.keys() :
        if BOOKMAKER_OFFSET[v].HAS_API :
            continue

        session_array = {}
        shutil.rmtree(SERVER_DATA_PATH + 'tmp_data/sessions')
        os.mkdir(SERVER_DATA_PATH + 'tmp_data/sessions')
        for client in data :
            if client['bookmaker'] == v :
                sess_info = BOOKMAKER_OFFSET[client['bookmaker']].create_session(
                    client['bookmaker_login'],
                    client['bookmaker_password']
                )
                with open(SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client['id']), 'wb') as f:
                    pickle.dump(sess_info['session'], f)
                    sess_info['session'] = SERVER_DATA_PATH + 'tmp_data/sessions/' + str(client['id'])

                session_array[client['id']] = sess_info

        with open(SERVER_DATA_PATH + 'betscsgo/sessions.json', 'w') as f:
            json.dump(session_array, f, indent=4)

if __name__ == '__main__' :
    main()
