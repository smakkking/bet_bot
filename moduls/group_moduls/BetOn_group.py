from moduls.bookmaker_moduls import BETSCSGO_betting

import bet_manage
import nltk
import logging


WALL_URL = 'https://vk.com/bett_on'
NAME = 'bet_on'
DOGON_AGGREGATOR = BETSCSGO_betting.NAME
TITLE = "BETON CS:GO | Прогнозы и ставки CSGO & DOTA 2"
BANK = 1.5e5

BET_TEMPLATES = BETSCSGO_betting.PHOTO_PARSING_TEMPLATES # + other bookmakers templates

# here may be other speciefic templates, so add them to BET_TEMPLATES
# like BET_TEMPLATES += [(template, parse)]

def check_templates(post, token) :
    for photo_url in post.photo_list :
        obj = bet_manage.YandexAPI_detection(photo_url, token)
        text = obj.text_detection()

        has_template = False
        for (tmp, parse) in BET_TEMPLATES :
            if tmp(text.upper()) :
                st = parse(photo_url, nltk.word_tokenize(text))
                post.coupon.add_bet(st)
                has_template = True
        if not has_template :
            logging.getLogger(NAME).info("no templates for: " + photo_url)
    dogon(post)
    if post.coupon.bets == [] :
        post.parse_bet = False


def dogon(post) :
    patterns = [
        'ДОГОН',
    ]
    target = post.text.upper()
    for x in patterns :
        if type(x) is tuple :
            res = True
            for cond in x :
                res = res and target.find(cond) >= 0
            if res :
                post.coupon.set_dogon()
                break
        elif type(x) is str and target.find(x) >= 0 :
            post.coupon.set_dogon()
            break