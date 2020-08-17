from bs4 import BeautifulSoup
import time
# ПЕРЕДЕЛАТЬ - УЕБАНЫ НА ПАРИМАТЧ CДЕЛАЛИ НОВУБ ВЕРСИЮ САЙТА БЕЗ ПОИСКА!!!!!!!!!!
import manage_file

BET_URL = 'https://new.parimatch.ru'

class Bookmaker() :
    def __init__(self, url) :
        self.main_url = url

class rushBet(Bookmaker) :
    def search_bet(self, stavka) :
        pass
    def bet(self, BROWSER, url, stavka):
        pass



