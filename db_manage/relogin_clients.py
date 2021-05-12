import shutil
import os

from global_links import BOOKMAKER_OFFSET
from global_constants import SERVER_DATA_PATH

from exe_scripts import scan_database


def main() :
    shutil.rmtree(SERVER_DATA_PATH + 'tmp_data/sessions')
    os.mkdir(SERVER_DATA_PATH + 'tmp_data/sessions')

    data = scan_database.main(mode='relogin')

    for v in BOOKMAKER_OFFSET.keys() :
        if BOOKMAKER_OFFSET[v].HAS_API :
            continue
        
        BOOKMAKER_OFFSET[v].relogin(data)

if __name__ == '__main__' :
    main()
