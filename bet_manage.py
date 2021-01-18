# общие модули
import sqlite3
import time
from sqlite3 import Error
import requests
import urllib
import base64
import re
import json
import os

# light selenium
from selenium import webdriver

# dark selenium
import undetected_chromedriver as uc

from global_constants import CHROME_DRIVER_PATH, CHROME_DIR_PACKAGES, DATABASE_PATH, ALL_POSTS_JSON_PATH


LOAD_TIMEOUT = 0.5  # sec


class Stavka :
    def __init__(self, bets=None) :

        self.bk_links = {}
        self.summ_multiplier = 1
        self.sum = 0

        if bets is None :
            self.match_title = ''
            self.winner = ''
            self.outcome_index = ''
            self.dogon = False
        else :
            self.match_title = bets['match_title']
            self.winner = bets['winner']
            self.outcome_index = bets['outcome_index']
            self.dogon = bets['dogon']
            self.summ_multiplier = bets['summ_multiplier']
            if 'sum' in bets.keys():
                self.sum = bets['sum']
            if 'bk_links' in bets.keys() :
                self.bk_links = bets['bk_links']

    def __eq__(self, other):
        flag = True
        flag &= self.match_title == other.match_title
        flag &= self.outcome_index == other.outcome_index
        flag &= self.winner == other.winner
        return flag

    def __json_repr__(self) :
        return self.__dict__

    def get_bk_link(self, bk_name):
        return self.bk_links[bk_name]

    def set_bk_link(self, bk_name, params={}):
        self.bk_links[bk_name] = params


class Coupon :
    def __init__(self, type_x='ordn', coup_data: dict=None) :
        self.bets = []
        self.dogon = []
        self.type = type_x
        if coup_data :
            self.type = coup_data['type']
            for bet in coup_data['bets'] :
                self.add_bet(Stavka(bet))
            for bet in coup_data['dogon'] :
                self.add_bet(Stavka(bet), to_dogon=True)

    def __json_repr__(self) :
        return dict([
            ('type', self.type),
            ('bets', [b.__json_repr__() for b in self.bets]),
            ('dogon', [b.__json_repr__() for b in self.dogon])
        ])
        
    def add_bet(self, bet, to_dogon=False) :
        if to_dogon :
            self.dogon.append(bet)
        else :
            self.bets.append(bet)

    def change_type(self, new_type) :
        self.type = new_type

    def set_dogon(self) :
        for b in self.bets :
            if type(b.outcome_index) is tuple and b.outcome_index[0].find('map') >= 0 :
                b.dogon = True
        pass


class LastGroupPost:

    token = 'b43bde71b43bde71b43bde7135b44ed5a0bb43bb43bde71eb83d753b1a8f54e925ecaec'
    ver = 5.92

    def __init__(self, wall_url : str, old=None) :
        self.text = ''
        self.photo_list = []
        self.parse_bet = True
        self.coupon = Coupon(coup_data=old)
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

    def __dict__(self):
        return dict([
            ('text', self.text),
            ('photo_list', self.photo_list),
            ('parse_bet', self.parse_bet),
            ('coupon', self.coupon),
        ])

    def __str__(self) :
        return str(self.__dict__)
        
    def get(self, offset=0, count=2) :
        # заполняет поля photo_list и text
        base_url = 'https://api.vk.com/method/wall.get'

        try :
            resp = requests.get(base_url, params={
                'access_token' : LastGroupPost.token,
                'v' : LastGroupPost.ver,
                'domain' : self.wall_domain,
                'count' : count,
                'offset' : offset,
            })
            posts = resp.json()['response']['items']
        except :
            assert False, "error in requesting group wall"

        if count == 2 :
            try :
                if 'is_pinned' in posts[0].keys() and posts[0]['is_pinned'] :
                    p = posts[1]
                else :
                    p = posts[0]
                self.text = p['text']
                if 'attachments' in p.keys() :
                    for at in p['attachments'] :
                        if at['type'] == 'photo' :
                            self.add_photo(at['photo']['sizes'][len(at['photo']['sizes']) - 1]['url'])
            except :
                assert False, "error in vk_api"
        else : 
            # для большого числа постов сохраяются только фото         
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
        from global_constants import GROUP_OFFSET
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

    def SQL_UPDATE(self, set_cond: str, where_cond: str) :

        if where_cond == '' or set_cond == '' :
            return

        query = "UPDATE " + SQL_DB.MODEL_NAME + '\n'
        query += "SET " + set_cond + '\n'
        query += "WHERE " + where_cond.replace('and', 'AND').replace('or', 'OR')

        self.execute_query(query)

    def __del__(self) :
        self.connection.close()


class YandexAPI_detection() :

    # иногда случается, что запрос на токен длится более 20 сек, как отлавливать - хз
    iam_token = ''
    oAuth_token = 'AgAAAAApv9blAATuwWZGhGvmrkzMm3hoRBzKIuE'
    folder_id = 'b1goeg4e1h56agdp1q9d'
    
    @classmethod
    def create_new_token(cls, debug=False) :
        data = {
            "yandexPassportOauthToken" : cls.oAuth_token
        }
        if debug :
            now = time.time() # замер времени

        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json=data)

        if debug :
            print(f'token collected in {time.time() - now : .2f} sec')       

        cls.iam_token = response.json()['iamToken']
    
    def __init__(self, photo_url, iam_token=None) :
        resource = None
        while resource is None :
            try :
                resource = urllib.request.urlopen(photo_url)
            except urllib.error.URLError :
                resource = None
        self.base64_img = base64.b64encode(resource.read())
        if iam_token :
            YandexAPI_detection.iam_token = iam_token
        
    def text_detection(self, debug=False) -> str :

        def get_text_from_response(resp : str) -> list :
            x = re.findall('\"text\":\s\".*\"', resp)
            return [k[k.find(':') + 3 : len(k) - 1] for k in x]
    
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + YandexAPI_detection.iam_token,
        }
        if debug :
            now = time.time() # замер времени
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
                ]
            })

        if debug :
            print(f'text detected in {time.time() - now : .2f} sec')

        return ' '.join(get_text_from_response(response.text))


def get_html_with_browser(browser, url, sec=0, cookies=None) :
    if url != 'none' :
        browser.get(url)
    if cookies :
        for cok in cookies :
            browser.add_cookie({
                'name' : cok[0],
                'value' : cok[1],
            })
    time.sleep(sec)

    return browser.page_source

def create_webdriver(user_id=None, undetected_mode=False, hdless=False) :
    if undetected_mode :
        opts = uc.ChromeOptions()
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + 'ID_' + user_id)
        opts.add_argument('--profile-directory=Profile_1')
        opts.set_headless(headless=hdless)
        obj = uc.Chrome(options=opts, executable_path=CHROME_DRIVER_PATH)
    else :
        opts = webdriver.ChromeOptions()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        if hdless :
            opts.add_argument('--headless')
        #opts.set_headless(headless=hdless)
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        if user_id :
            opts.add_argument('--user-data-dir=' + CHROME_DIR_PACKAGES + 'ID_' + user_id)
        opts.add_argument("--disable-dev-shm-usage")

        opts.add_argument('--profile-directory=Profile_1')
        obj = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=opts)
    obj.implicitly_wait(LOAD_TIMEOUT)

    return obj
    
# return 'left' or 'right'
def define_side_winner(url) :

    from PIL import Image
    import requests

    def otkl(color) :
        # если честно сомнительное сравнение
        # возможно нужно сузить диапазон цветов

        flag = True
        green_upper = (255, 255, 91)
        green_lower = (110, 85, 40)
        for i in range(len(color)) :
            flag &= green_lower[i] <= color[i] <= green_upper[i]
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

    if count_right > count_left:
        return 'right'
    else:
        return 'left'

def reform_team_name(s : str) :
    s = s.replace(' ', '')
    s = s.upper()
    return s

def read_groups() :

    file_is_available(ALL_POSTS_JSON_PATH)
    with open(ALL_POSTS_JSON_PATH, 'r', encoding="utf-8") as last_posts_json:
        DATA = json.load(last_posts_json)

    for key in DATA.keys() :
        DATA[key]['coupon'] = Coupon(coup_data=DATA[key]['coupon'])

    return DATA


def write_groups(t) :
    for x in t.keys() :
        t[x]['coupon'] = t[x]['coupon'].__json_repr__()

    file_is_available(ALL_POSTS_JSON_PATH)

    with open(ALL_POSTS_JSON_PATH, 'w', encoding="utf-8") as last_posts_json :
        json.dump(t, last_posts_json, indent=4)


def file_is_available(file) :
    counter = 0
    while True:
        try:
            os.rename(file, file)
            break
        except OSError:
            print(f"{counter} tries to pass")
            continue
