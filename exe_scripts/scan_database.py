from bet_manage import SQL_DB

from global_constants import SERVER_DATA_PATH, BASE_GROUP_PAYMENT, BET_COMISSION
from global_links import GROUP_OFFSET


def main(mode='all_bet', payment={}):
    """mode = 'all_bet' || 'relogin'"""
    a = SQL_DB(SERVER_DATA_PATH)

    if mode == 'all_bet':
        if payment:
            b = a.SQL_SELECT(
                ['id', 'personal_count'],
                where_cond='sub_status=1 and bot_status=1'
            )
            improve_list = []
            for x in b:
                if x['id'] in payment.keys():
                    x['personal_count'] -= payment[x['id']] * BET_COMISSION
                    improve_list.append(x)

            for x in improve_list:
                mode_str = "personal_count={},bot_status={}".format(
                    x['personal_count'], 1 if x['personal_count'] > 0 else 0)
                a.SQL_UPDATE(
                    mode_str,
                    f"id={x['id']}"
                )

        else:
            return a.SQL_SELECT(
                ['bookmaker', 'bet_mode', 'bet_summ', 'id'],
                where_cond='sub_status=1 and bot_status=1',
                groups_query=True
            )
    elif mode == 'relogin':
        b = a.SQL_SELECT(
            ['id', 'personal_count'],
            where_cond='sub_status=1',
            groups_query=True
        )

        for x in b:
            mode_str = ""
            for group in GROUP_OFFSET.keys():
                if group in x['groups']:
                    # вычитается базовая стоимость группы
                    x['personal_count'] -= BASE_GROUP_PAYMENT
                    mode_str += "is_{}=1,".format(group)
                else:
                    mode_str += "is_{}=0,".format(group)

            a.SQL_UPDATE(
                mode_str + "personal_count={}".format(x['personal_count']),
                "id={}".format(x['id'])
            )

        return a.SQL_SELECT(
            ['bookmaker', 'id', 'bookmaker_login', 'bookmaker_password'],
            where_cond='sub_status=1',
        )


if __name__ == "__main__":
    t = main()
