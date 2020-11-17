import load_last_data, scan_database, all_bet
import manage
import time

RETIME_CYCLE = 30

def time_loop(last) :
    sec = time.time() - last
    if sec < RETIME_CYCLE :
        time.sleep(RETIME_CYCLE - sec)

if __name__ == "__main__" :
    #while (True) :
    now = time.time()
    load_last_data.main()
    client_data = scan_database.main()
    all_bet.main(client_data)
    time_loop(now)
