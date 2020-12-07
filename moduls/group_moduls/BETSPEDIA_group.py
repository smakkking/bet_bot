from moduls.bookmaker_moduls import BETSCSGO_betting

import bet_manage
import nltk

WALL_URL = 'https://vk.com/betspedia_csgo'
NAME = 'BetsPedia'

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
    # TODO переделать с такой же функцией только у модуля группы
    post.find_dogon()
    if post.coupon.bets == [] :
        post.parse_bet = False