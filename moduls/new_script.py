# строка для правильной работы импортирования пакетов
import sys
sys.path[0] = sys.path[0][ : sys.path[0].find('bet_bot') + 7]

from selenium import webdriver
from datetime import datetime

import time
from datetime import datetime

from moduls import manage_file
from moduls.bookmaker_moduls import parimatch_betting
    
if __name__ == '__main__' :
    