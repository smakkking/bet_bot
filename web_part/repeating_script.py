from EXE_scripts import load_last_data, scan_database, all_bet
import manage
import time

RETIME_CYCLE = 1 # min

def time_loop(last) :
    sec = time.time() - last
    print(f'{sec} seconds passed after beggining of a script-run.')
    if sec < RETIME_CYCLE * 60:
        time.sleep(RETIME_CYCLE * 60 - sec)

if __name__ == "__main__" :
    for _ in range(1) :
        now = time.time()
        load_last_data.main()
        #client_data = scan_database.main()
        #all_bet.main(client_data)
        time_loop(now)
