from bet_manage import SQL_DB
from datetime import datetime

def main() :
    a = SQL_DB()
    d = a.SQL_SELECT(select_cond=['sub_end_date', 'id'], groups_query=False, where_cond='sub_status=1')

    change_sub_status = ''
    for rec in d :
        if datetime.today() > datetime.strptime(rec['sub_end_date'], "%Y-%m-%d") :
            change_sub_status += "id = " + str(rec['id']) + ' or '
    change_sub_status = change_sub_status[ : len(change_sub_status) - 4]

    a.SQL_UPDATE(set_cond='sub_status=0, sub_end_date=null, max_group_count=0', where_cond=change_sub_status)


if __name__ == "__main__":
    main()
