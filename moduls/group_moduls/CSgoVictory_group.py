WALL_URL = 'https://vk.com/victorybets_stavki'
NAME = 'CSgoVictory'

from moduls.bookmaker_moduls import BETSCSGO_betting

import bet_manage
import nltk

BET_TEMPLATES = BETSCSGO_betting.PHOTO_PARSING_TEMPLATES # + other bookmakers templates

# here may be other speciefic templates, so add them to BET_TEMPLATES
# like BET_TEMPLATES += [(template, parse)]

def check_templates(post, token) :
    for photo_url in post.photo_list :
        obj = bet_manage.YandexAPI_detection(photo_url, token)
        text = obj.text_detection()
        for (tmp, parse) in BET_TEMPLATES :
            if tmp(text.upper()) :
                st = parse(photo_url, nltk.word_tokenize(text))
                post.coupon.add_bet(st)
    dogon(post)
    if post.coupon.bets == [] :
        post.parse_bet = False


def dogon(post) :
    patterns = [
        'ДОГОН',
    ]
    target = post.text.upper()
    for x in patterns :
        if target.find(x) >= 0 :
            post.coupon.set_dogon()
            break