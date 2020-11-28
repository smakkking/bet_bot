from EXE_scripts import load_last_data, scan_database, all_bet
import manage
import time

# осуществляет непосредственно ставочный процесс для всех клиентов
# работает круглосуточно


if __name__ == "__main__" :
    now = time.time()
    #load_last_data.main()
    client_data = scan_database.main()
    print(client_data)
    all_bet.main(client_data)

