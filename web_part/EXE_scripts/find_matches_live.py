from moduls.bet_manage import BOOKMAKER_OFFSET

def main() :
    for v in BOOKMAKER_OFFSET.values() :
        if not v.TAKES_MATHES_LIVE :
            v.find_bet()