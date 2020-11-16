# общие модули
from bs4 import BeautifulSoup

import sys
import time
from datetime import datetime
import os

# light selenium
from selenium import webdriver
from selenium import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# dark selenium
import undetected_chromedriver as uc

from manage import CHROME_DRIVER_PATH, CHROME_DIR_PACKAGES
from moduls.bookmaker_moduls import BETSCSGO_betting
from moduls.group_moduls import ExpertMnenie_group

GROUP_OFFSET = {
    ExpertMnenie_group.NAME : ExpertMnenie_group,

}

BOOKMAKER_OFFSET = {
    BETSCSGO_betting.NAME : BETSCSGO_betting,
    
}

class Stavka :
    def __init__(self, bets=None) :
        if bets == None :
            self.summ = '0'
            self.match_title = ''
            self.winner = ''
            self.outcome_index = ''
        else :
            for key, value in bets.items() :
                setattr(self, key, value)

    def change_summ(self, s : int) :
        self.summ = str(s)

    def __repr__(self) :
        return str(self.__dict__)


class Coupon() :
    def __init__(self, type_x='ordn', coup_data = None) :
        self.bets = []
        if (coup_data == None) :
            self.type = type_x
        else :
            self.type = coup_data['type']
            for bet in coup_data['bets'] :
                self.bets.append(Stavka(bet))

    def __json_repr__(self) :
        return self.__dict__
        
    def add_bet(self, bet) :
        self.bets.append(bet)

    def change_type(self, new_type) :
        self.type = new_type


class LastGroupPost() :
    def __init__(self) :
        self.text = ''
        self.photo_list = []
        self.parse_bet = True
        self.coupon = Coupon()

    def add_photo(self, photo) :
        self.photo_list.append(photo)

    def __json_repr__(self) :
        return dict([('text', self.text), ('photo_list', self.photo_list), ('parse_bet', self.parse_bet), ('coupon', self.coupon.__json_repr__())])
        
    def get(self, BROWSER, url) :
        get_html_with_browser(BROWSER, url)
        # первый пост
        first_post = BROWSER.find_element_by_id('page_wall_posts').find_element_by_tag_name('div').find_element_by_class_name('wall_text')
        # получаем текст
        self.text = first_post.find_elements_by_tag_name('div')[1].text
        # получаем список фото
        try :
            photos_click_dom = first_post.find_elements_by_tag_name('div')[2].find_elements_by_tag_name('a')
        except IndexError :
            photos_click_dom = []

        try :
            for item in photos_click_dom :
                item.click()
                time.sleep(0.5) # подумать над временем
                self.add_photo(BROWSER.find_element_by_xpath('//*[@id="pv_photo"]/img').get_attribute('src'))
                BROWSER.find_element_by_class_name('pv_close_btn').click() # нужно закрыть фото
                time.sleep(0.5) # подумать над временем
        except common.exceptions.NoSuchElementException:
            pass
    
def get_html_with_browser(BROWSER, url, sec=0) :
    if url != 'none' :
        BROWSER.get(url)
    time.sleep(sec)
    return BROWSER.page_source

def get_text_from_image(BROWSER, url) :
    # нужны ли исключения?
    base_url = 'https://yandex.ru/images'
    get_html_with_browser(BROWSER, base_url, 1)
    try :
        btn1 = BROWSER.find_element_by_xpath("/html/body/header/div/div[2]/div[1]/form/div[1]/span/span/div[2]/button")
        btn1.click()
    except :
        assert False, "Can't find btn1"
    time.sleep(0.5)
    try :
        inp = BROWSER.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/form[2]/span/span/input")
        inp.send_keys(url)
    except :
        assert False, "Can't find input"
    time.sleep(0.5)
    try :
        btn2 = BROWSER.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/form[2]/button")
        btn2.click()
    except:
        assert False, "Can't find btn2"

    time.sleep(3)

    soup = BeautifulSoup(BROWSER.page_source, 'html.parser')
    items2 = soup.find_all('div', class_='CbirOcr-TextBlock CbirOcr-TextBlock_level_text')
    text = []
    for item in items2 :
       text.append(item.text)
    return text

def create_webdriver(user_id='', undetected_mode=False) :
    if undetected_mode :
        opts = uc.ChromeOptions()
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + r'\ID_' + user_id)
        else :
            opts.add_argument('--user-data-dir=' + r'C:\Users\user1\AppData\Local\Google\Chrome\TEST')
        opts.add_argument('--profile-directory=Profile_1')
        obj = uc.Chrome(options=opts, enable_console_log=False)
        return obj
    else :
        opts = Options()
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + r'\ID_' + user_id)
        else :
            opts.add_argument('--user-data-dir=' + r'C:\Users\user1\AppData\Local\Google\Chrome\TEST')
        opts.add_argument('--profile-directory=Profile_1') 
        obj = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=opts)
        return obj
    
# return 'left' or 'right'
def define_side_winner(url) :
    from PIL import Image
    import requests

    def otkl(color) :
        flag = True
        green = (182, 235, 52)
        for i in range(len(color)) :
            flag = flag and abs(color[i] - green[i]) < 2
        return flag

    resp = requests.get(url, stream=True).raw
    image = Image.open(resp)

    obj = image.load()
    w, h = image.size
    green_array = []
    for x in range(w) :
        for y in range(h) :
            if otkl(obj[x, y]) :
                green_array.append((x, y))

    count_left = 0
    count_right = 0          
    for (x, y) in green_array :
        if x < w / 2 :
            count_left += 1
        else :
            count_right += 1

    if count_right == len(green_array) :
        return 'right'
    elif  count_left == len(green_array) :
        return 'left'