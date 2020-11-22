# общие модули
from bs4 import BeautifulSoup
import sys, time
from datetime import datetime
import sqlite3, os
from sqlite3 import Error
import requests, urllib, base64
import re

# light selenium
from selenium import webdriver
from selenium import common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# dark selenium
import undetected_chromedriver as uc

from manage import CHROME_DRIVER_PATH, CHROME_DIR_PACKAGES, DATABASE_PATH
from moduls.bookmaker_moduls import BETSCSGO_betting
from moduls.group_moduls import ExpertMnenie_group, CSgoVictory_group

GROUP_OFFSET = {
    ExpertMnenie_group.NAME : ExpertMnenie_group,
    CSgoVictory_group.NAME : CSgoVictory_group,
}

BOOKMAKER_OFFSET = {
    BETSCSGO_betting.NAME : BETSCSGO_betting,
}

LOAD_TIMEOUT = 30 # sec

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

    def __json_repr__(self) :
        return self.__dict__


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
        return dict([('type', self.type), ('bets', [b.__json_repr__() for b in self.bets])])
        
    def add_bet(self, bet) :
        self.bets.append(bet)

    def change_type(self, new_type) :
        self.type = new_type


class LastGroupPost() :

    token = 'b43bde71b43bde71b43bde7135b44ed5a0bb43bb43bde71eb83d753b1a8f54e925ecaec'
    ver = 5.92

    def __init__(self, wall_url : str) :
        self.text = ''
        self.photo_list = []
        self.parse_bet = True
        self.coupon = Coupon()
        self.wall_domain = wall_url[wall_url.rfind('/') + 1 : ]

    def add_photo(self, photo) :
        self.photo_list.append(photo)

    def __json_repr__(self) :
        return dict([
            ('text', self.text), 
            ('photo_list', self.photo_list), 
            ('parse_bet', self.parse_bet), 
            ('coupon', self.coupon.__json_repr__()),
        ])

    def __str__(self) :
        return str(self.__dict__)
        
    def get(self, offset=0, count=2) :
        base_url = 'https://api.vk.com/method/wall.get'

        resp = requests.get(base_url, params={
            'access_token' : LastGroupPost.token,
            'v' : LastGroupPost.ver,
            'domain' : self.wall_domain,
            'count' : count,
            'offset' : offset,
        })

        posts = resp.json()['response']['items']
        if count == 2 :
            if 'is_pinned' in posts[0].keys() and posts[0]['is_pinned'] :
                p = posts[1]
            else :
                p = posts[0]
            self.text = p['text']
            if 'attachments' in p.keys() :
                for at in p['attachments'] :
                    if at['type'] == 'photo' :
                        self.add_photo(at['photo']['sizes'][len(at['photo']['sizes']) - 1]['url'])
        else :           
            for p in posts :
                if 'attachments' in p.keys() :
                    for at in p['attachments'] :
                        if at['type'] == 'photo' :
                            self.add_photo(at['photo']['sizes'][len(at['photo']['sizes']) - 1]['url'])


class SQL_DB():

    MODEL_NAME = 'UserDataManagment_standartuser'

    def __init__(self) :
        self.connection = sqlite3.connect(DATABASE_PATH)

    def execute_query(self, query) :
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except Error as e:
            print(f"query is not correct, because of {e}")
        self.connection.commit()
        return result
    
    def SQL_SELECT(self, select_cond : list, where_cond : str=None, groups_query=False) :
        select_users = "SELECT"
        for arg in select_cond :
            select_users += ', ' + arg
        if groups_query :
            for group in GROUP_OFFSET.keys() :
                select_users += ', ' + group
        select_users = select_users.replace(',', '', 1) + '\n'

        select_users += 'FROM ' + SQL_DB.MODEL_NAME + '\n'

        if where_cond != None :
            select_users += 'WHERE ' + where_cond.replace('and', 'AND').replace('or', 'OR')
    
        users = self.execute_query(select_users)

        result = []
        for user in users :
            dic = {}
            for i in range(len(select_cond)) :
                dic[select_cond[i]] = user[i]

            if groups_query :
                p = []
                i = 0
                for value in GROUP_OFFSET.keys() :
                    if user[i + len(select_cond)] :
                        p.append(value)
                    i += 1
                dic['groups'] = p
            result.append(dic)  

        return result

    def SQL_UPDATE(self, set_cond : str, where_cond : str) :

        if where_cond == '' or set_cond == '' :
            return

        query = "UPDATE " + SQL_DB.MODEL_NAME + '\n'
        query += "SET " + set_cond + '\n'
        query += "WHERE " + where_cond.replace('and', 'AND').replace('or', 'OR')
        
        self.execute_query(query)

    def __del__(self) :
        self.connection.close()


class YandexAPI_detection() :

    iam_token = ''
    oAuth_token = 'AgAAAAApv9blAATuwWZGhGvmrkzMm3hoRBzKIuE'
    folder_id = 'b1goeg4e1h56agdp1q9d'
    
    @classmethod
    def create_new_token(cls) :
        data = {
            "yandexPassportOauthToken" : cls.oAuth_token
        }
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json=data)
        cls.iam_token = response.json()['iamToken']
    
    def __init__(self, photo_url) :
        resource = urllib.request.urlopen(photo_url)
        self.base64_img = base64.b64encode(resource.read())
        
    def text_detection(self) -> str :

        def get_text_from_response(resp : str) -> list :
            x = re.findall('\"text\":\s\".*\"', resp)
            return [k[k.find(':') + 3 : len(k) - 1] for k in x]
    
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + YandexAPI_detection.iam_token,
        }
        now = time.time()
        response = requests.post('https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze', headers=headers, json={
                'folderId': YandexAPI_detection.folder_id,
                'analyzeSpecs': [
                    {
                        'content': self.base64_img.decode('utf-8'),
                        'features': [
                            {
                                'type': 'TEXT_DETECTION',
                                'textDetectionConfig': {'languageCodes': ['*']}
                            }
                        ],
                    }
                ]})

        print(f'detected in {time.time() - now} sec')
        return ' '.join(get_text_from_response(response.text))




def get_html_with_browser(BROWSER, url, sec=0) :
    if url != 'none' :
        BROWSER.get(url)
    return BROWSER.page_source

def get_text_from_image(BROWSER, url) :
    # нужны ли исключения?
    base_url = 'https://yandex.ru/images/search'

    response = requests.get(base_url, params= {
        'source' : 'collections',
        'rpt' : 'imageview',
        'url' : url
    })
    
    get_html_with_browser(BROWSER, response.url)
    BROWSER.find_element_by_class_name('Fold-Body')

    soup = BeautifulSoup(BROWSER.page_source, 'html.parser')
    items2 = soup.find_all('div', class_='CbirOcr-TextBlock CbirOcr-TextBlock_level_text')
    text = []
    for item in items2 :
       text.append(item.text)
    return text

def create_webdriver(user_id='', undetected_mode=False, hdless=False) :
    if undetected_mode :
        opts = uc.ChromeOptions()
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + r'\ID_' + user_id)
        opts.add_argument('--profile-directory=Profile_1')
        opts.set_headless(headless=hdless)
        obj = uc.Chrome(options=opts, executable_path=CHROME_DRIVER_PATH)
    else :
        opts = webdriver.ChromeOptions()
        opts.set_headless(headless=hdless)
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + r'\ID_' + user_id)
        opts.add_argument('--profile-directory=Profile_1')         
        obj = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=opts)
    obj.implicitly_wait(LOAD_TIMEOUT)
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