from exe_scripts import relogin_live, load_last_data, scan_database, all_bet, find_matches_live

# осуществляет непосредственно ставочный процесс для всех клиентов
# работает круглосуточно

if __name__ == "__main__" :
    # выполнятются редко
    find_matches_live.main(debug=True)
    relogin_live.main(debug=True)

    # выполняются постоянно
    load_last_data.main(debug=True)
    client_data = scan_database.main()
    all_bet.main(client_data, debug=True)



